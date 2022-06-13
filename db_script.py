from peewee import *
import report.report as rep
import os

path_to_files = os.path.join(os.path.dirname(__file__), './data')

db = SqliteDatabase('racer.db')


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


def fill_db():
    db.connect()
    db.drop_tables([Racer, RacerTime])
    db.create_tables([Racer, RacerTime])
    for racer in rep.build_report(path_to_files):
        racer_inst = Racer(
            driver_id=racer.abb,
            name=racer.name,
            team=racer.team)
        racer_time_inst = RacerTime(
            racer=racer_inst,
            start_time=racer.start_time,
            end_time=racer.end_time,
            best_lap=racer.best_lap,
        )
        racer_inst.save()
        racer_time_inst.save()
    db.close()


if __name__ == '__main__':
    fill_db()