from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "promocodes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "code" VARCHAR(50) NOT NULL UNIQUE,
    "study" BOOL NOT NULL  DEFAULT False,
    "one_time" BOOL NOT NULL  DEFAULT False,
    "multiple_use" BOOL NOT NULL  DEFAULT False,
    "eternal" BOOL NOT NULL  DEFAULT False,
    "max_activations" INT NOT NULL  DEFAULT 1,
    "activations_count" INT NOT NULL  DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "sysdata" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "currency" VARCHAR(10) NOT NULL,
    "exchange_currency" VARCHAR(10) NOT NULL,
    "exchange_rate" DECIMAL(10,4) NOT NULL,
    "graduation_step" DECIMAL(10,4) NOT NULL
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(255) NOT NULL UNIQUE,
    "user_id" BIGINT NOT NULL UNIQUE,
    "first_name" VARCHAR(255),
    "description" VARCHAR(255),
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "is_staff" BOOL NOT NULL  DEFAULT False,
    "date_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "orders" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "order_id" INT NOT NULL UNIQUE,
    "status" VARCHAR(11) NOT NULL  DEFAULT 'Создан',
    "contact_method" VARCHAR(255),
    "currency" VARCHAR(10) NOT NULL  DEFAULT 'Rub',
    "amount" DECIMAL(10,2) NOT NULL,
    "exchange_currency" VARCHAR(10) NOT NULL,
    "exchange_rate" DECIMAL(10,4) NOT NULL,
    "date_created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "orders"."status" IS 'CREATING: Создан\nPROCESSING: В обработке\nCOMPLETED: Выполнен\nCANCELED: Отменен';
CREATE TABLE IF NOT EXISTS "user_activities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "activity_type" VARCHAR(255) NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT REFERENCES "users" ("id") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
