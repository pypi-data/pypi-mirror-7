﻿-- Триггерная процедура заполнения и партиционирования при вставке

CREATE OR REPLACE FUNCTION warehouses_stock_tfunc_before_insert()
  RETURNS trigger AS
$BODY$
DECLARE
    INCOMING   CONSTANT char := '+';
    OUTCOMING  CONSTANT char := '-';
    MOVING_OUT CONSTANT char := '<';
    MOVING_IN  CONSTANT char := '>';
    INVENTORY  CONSTANT char := '=';
    sign            real := 1.0;
    pre_stock_count real := 0.0;
    diff_for_post   real := 0.0;
    post_inner record;
    pre_stock  record;

    _year       integer;
    _table_info record;
    _table_name varchar;
    _index_name varchar;
    _year_start varchar;
    _year_end   varchar;
BEGIN
    -- test
    RAISE DEBUG 'run %', TG_NAME;

    --*-- ПРОВЕРКА ВХОДНЫХ ПАРАМЕТРОВ --*--

    -- Если это не подходящий тип документа, то прервать вставку, вернув NULL
    IF NEW.kind NOT IN (INCOMING, OUTCOMING, MOVING_OUT, MOVING_IN, INVENTORY) THEN
        RETURN NULL;
    --Если отсутвует дата-время по документу
    ELSIF NEW.date_time IS NULL THEN
        RAISE EXCEPTION 'Unavailable datetime in the document.';
    END IF;

    -- Сбрасываем флаг на всякий случай
    NEW._trigger_lock := FALSE;

    -- Если это не инвентаризация
    IF NEW.kind != INVENTORY THEN
        --Если отсутвует количество по документу
        IF NEW.doc_count IS NULL THEN
            RAISE EXCEPTION 'Unavailable quantity in the document.';
        END IF;

        -- Если это приход
        IF NEW.kind = INCOMING THEN
            -- Если отсутвует цена и сумма по документу
            IF NEW.doc_price IS NULL AND NEW.doc_summa IS NULL THEN
                RAISE EXCEPTION 'Unavailable price and sum in the document.';
            ELSE
                -- Если отсутвует цена по документу
                IF NEW.doc_price IS NULL THEN
                    -- то расчитываем цену по сумме
                    RAISE NOTICE 'SET doc_price by doc_summa.';
                    IF NEW.doc_count != 0 THEN
                        NEW.doc_price := 1.0 * NEW.doc_summa / NEW.doc_count;
                    ELSE
                        NEW.doc_price := 0.0;
                    END IF;
                ELSE
                    -- иначе расчитываем сумму по цене
                    RAISE NOTICE 'SET doc_summa by doc_price.';
                    NEW.doc_summa := NEW.doc_price * NEW.doc_count;
                END IF;
            END IF;
        -- Если это перемещение на склад
        ELSIF NEW.kind = MOVING_IN THEN 
            -- Если отсутвует цена или сумма по документу, или нет 
            -- ссылки на строку перемещения со склада
            IF NEW.doc_price IS NULL OR NEW.doc_summa IS NULL OR NEW.parent_id IS NULL THEN
                RAISE EXCEPTION 'Unavailable transfer from a warehouse in the document.';
            END IF;
        -- Если это не расход и не перемещение со склада
        ELSIF NOT NEW.kind IN (OUTCOMING, MOVING_OUT) THEN 
            RAISE EXCEPTION 'The wrong type of document.';
        END IF;

    END IF;

    --*-- ОБРАБОТКА ОСТАЛЬНЫХ ПОЛЕЙ СТРОКИ --*--

    -- Получить предыдущую строку остатков
    SELECT * INTO pre_stock FROM warehouses_stock i
    WHERE
        i.nomenclature_id = NEW.nomenclature_id
        AND i.warehouse_id = NEW.warehouse_id
        AND i.id != NEW.id
        AND (i.date_time < NEW.date_time OR (i.date_time = NEW.date_time AND i.id < NEW.id))
    ORDER BY i.date_time DESC, i.id DESC
    LIMIT 1;

    -- УСТАНОВКА ЦЕН --

    IF FOUND THEN
        pre_stock_count := pre_stock.count;
        RAISE DEBUG 'pre_stock_count=%', pre_stock.count;
        RAISE DEBUG 'pre_stock.id=%,', pre_stock.id;
        -- Если это приход или перемещение на склад
        IF NEW.kind IN (INCOMING, MOVING_IN) THEN
            -- то установить усреднённую цену остатков,
            -- если остаток больше нуля
            IF (NEW.doc_count + pre_stock.count) > 0 AND (pre_stock.summa > 0) THEN
                NEW.price := 1.0 * (NEW.doc_summa + pre_stock.summa) / (NEW.doc_count + pre_stock.count);
            ELSE
                NEW.price := NEW.doc_price;
                -- TODO: наверное сделать поле для извещения
                -- пользователя о том, что остатки и цены отрицательные
            END IF;
        -- Если это расход или перемещение со склада или инвентаризация
        ELSIF NEW.kind in (OUTCOMING, MOVING_OUT, INVENTORY) THEN
            -- то установить цену в документе и на остатках по последним остаткам
            NEW.doc_price := pre_stock.price;
            NEW.price     := pre_stock.doc_price;
        ELSE
            RAISE EXCEPTION 'The wrong type of document.';
        END IF;
    ELSE
        pre_stock_count := 0.0;
        RAISE DEBUG 'pre_stock_count=0.0';
        RAISE DEBUG 'pre_stock.id=NULL';
        -- Если это приход или перемещение на склад
        IF NEW.kind in (INCOMING, MOVING_IN) THEN
            -- то установить цену остатков по самому поступлению
            NEW.price := NEW.doc_price;
        -- Если это расход или перемещение со склада или инвентаризация
        ELSIF NEW.kind in (OUTCOMING, MOVING_OUT, INVENTORY) THEN
            -- то установить цену в документе и на остатках равными нулю
            NEW.doc_price := 0.0;
            NEW.price     := 0.0;
        ELSE
            RAISE EXCEPTION 'The wrong type of document.';
        END IF;
    END IF;

    -- УСТАНОВКА КОЛИЧЕСТВА --

    -- Если это инвентаризация
    IF NEW.kind = INVENTORY THEN
        -- Если нет NEW.doc_count
        IF NEW.doc_count IS NULL THEN
            -- то устанавливаем количество по последним остаткам
            NEW.doc_count  := pre_stock_count;
            NEW.count      := pre_stock_count;
            NEW.diff       := 0.0;
        ELSE
            -- устанавливаем различия количества с последними остатками
            NEW.count := NEW.doc_count;
            NEW.diff  := NEW.count - pre_stock_count;
        END IF;
    -- Иначе если это расход или перемещение со склада
    ELSIF NEW.kind in (OUTCOMING, MOVING_OUT) THEN
        -- то устанавливаем количество за вычетом кол-ва по документу
        NEW.count := pre_stock_count - NEW.doc_count;
    -- Иначе если это приход или перемещение на склад
    ELSIF NEW.kind in (INCOMING, MOVING_IN) THEN
        -- то устанавливаем суммарное количество остатков
        NEW.count :=  pre_stock_count + NEW.doc_count;
    ELSE
        RAISE EXCEPTION 'The wrong type of document.';
    END IF;

    -- УСТАНОВКА СУММ --

    -- Установить сумму остатков и сумму по документу
    NEW.doc_summa := NEW.doc_price * NEW.doc_count;
    NEW.summa     := NEW.price * NEW.count;
    IF NEW.kind = INVENTORY THEN
        NEW.diff_summa := NEW.diff * NEW.price;
    END IF;

    --*-- ПАРТИЦИОНИРОВАНИЕ --*--

    _year := date_part('year', NEW.date_time);
    _year_start := _year || '-01-01 00:00:00+00:00';
    _year_end := _year+1 || '-01-01 00:00:00+00:00';
    _table_name := 'warehouses_stock_' || _year;
    _index_name := _table_name || '_date_time';

    SELECT * INTO _table_info FROM "information_schema"."tables"
    WHERE "table_name" = _table_name;

    IF NOT FOUND THEN
        EXECUTE 'CREATE TABLE '|| quote_ident(_table_name) || ' (
               CHECK ("date_time" >= TIMESTAMP ' || quote_literal(_year_start) || ' AND
                      "date_time"  < TIMESTAMP ' || quote_literal(_year_end) || ')
            )
            INHERITS ("warehouses_stock");';
        EXECUTE 'ALTER TABLE ' || quote_ident(_table_name)
            || ' ADD CONSTRAINT ' || quote_ident(_table_name || '_pkey')
            || ' PRIMARY KEY (id)';

        EXECUTE 'CREATE TRIGGER ' || quote_ident(_table_name || '_before_update')
            || ' BEFORE UPDATE ON ' || quote_ident(_table_name)
            || ' FOR EACH ROW EXECUTE PROCEDURE
                warehouses_stock_tfunc_before_update();';
        EXECUTE 'CREATE TRIGGER ' || quote_ident(_table_name || '_after_insert_or_delete')
            || ' AFTER INSERT OR DELETE ON ' || quote_ident(_table_name)
            || ' FOR EACH ROW EXECUTE PROCEDURE
                warehouses_stock_tfunc_after_insert_or_delete();';

        EXECUTE 'CREATE INDEX ' || quote_ident(_table_name || '_date_time')
            || ' ON ' || quote_ident(_table_name) || ' ("date_time")';
        EXECUTE 'CREATE INDEX ' || quote_ident(_table_name || '_kind')     
            || ' ON ' || quote_ident(_table_name) || ' ("kind");';
        EXECUTE 'CREATE INDEX ' || quote_ident(_table_name || '_kind_like')
            || ' ON ' || quote_ident(_table_name) || ' ("kind" varchar_pattern_ops);';
        EXECUTE 'CREATE INDEX ' || quote_ident(_table_name || '_document_id')
            || ' ON ' || quote_ident(_table_name) || ' ("document_id");';
        EXECUTE 'CREATE INDEX ' || quote_ident(_table_name || '_warehouse_id')
            || ' ON ' || quote_ident(_table_name) || ' ("warehouse_id");';
        EXECUTE 'CREATE INDEX ' || quote_ident(_table_name || '_nomenclature_id')
            || ' ON ' || quote_ident(_table_name) || ' ("nomenclature_id");';
    END IF;

    EXECUTE 'INSERT INTO ' || quote_ident(_table_name) || ' VALUES ($1.*)' USING NEW;

    RETURN NULL;
END;
$BODY$
LANGUAGE 'plpgsql';

-- DROP TRIGGER warehouses_stock_before_insert ON warehouses_stock;
CREATE TRIGGER warehouses_stock_before_insert
  BEFORE INSERT
  ON warehouses_stock
  FOR EACH ROW
  EXECUTE PROCEDURE warehouses_stock_tfunc_before_insert();
