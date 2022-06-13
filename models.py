from peewee import *


db = SqliteDatabase(None)


class BaseModel(Model):

    class Meta:
        database = db


class Racer(BaseModel):
    driver_id = CharField()
    name = CharField()
    team = CharField()

    class Meta:
        table_name = 'racer_data'


class RacerTime(BaseModel):
    racer = ForeignKeyField(Racer, column_name='driver_id')
    start_time = DateTimeField()
    end_time = DateTimeField()
    best_lap = CharField(null=True)

    class Meta:
        table_name = 'racer_time'
