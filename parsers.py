from flask_restful import reqparse


class Parsers:
    @staticmethod
    def users_parser(required: bool) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=required)
        parser.add_argument('surname', required=required)
        parser.add_argument('age', required=required, type=int)
        parser.add_argument('position', required=required)
        parser.add_argument('speciality', required=required)
        parser.add_argument('address', required=required)
        parser.add_argument('email', required=required)
        parser.add_argument('password', required=required)

        return parser

    @staticmethod
    def jobs_parser(required: bool) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument('job', required=required)
        parser.add_argument('team_leader', required=required, type=int)
        parser.add_argument('work_size', required=required, type=int)
        parser.add_argument('collaborators', required=required)
        parser.add_argument('is_finished', required=required, type=bool)
        return parser
