import argparse
import json
import os
import shutil
import sys

from triplander.models import City, Country, Region

FILE_PATH = 'triplander/dumps/latest.json.bz2'

#import logging
#log = logging.getLogger("mongokit.document")
#log.addHandler(logging.FileHandler("/tmp/porcozio.log"))


def migrate_country(entry):
    """
    Migration of a JSON-represented country.
    """
    try:
        corresp_map = {
            'code': entry['fields']['code'],
            'wikiname': entry['fields']['wikiname'],
            'currency': entry['fields']['currency'],
            'slug': entry['fields']['slug'],
            'name': entry['fields']['name'],
        }
        additional_corresp_map = {
            'old_pk': entry['pk'],
            'old_capitalcity_pk': entry['fields']['capital_city'],
        }

    except KeyError:
        raise RuntimeError(u"Invalid JSON configuration: %s" % str(entry))

    country = Country.find_one({'code': entry['fields']['code']})
    if not country:
        country = Country()

    country.set_lang("en")
    for k, v in corresp_map.iteritems():
        setattr(country, k, v)

    for k, v in additional_corresp_map.iteritems():
        country[k] = v

    country.save()
    return country


def migrate_city(entry):
    """
    Migration of a JSON-represented city.
    """
    corresp_map = {
        'wikiname': entry['fields']['wikiname'],
        'slug': entry['fields']['slug'],
        'name': entry['fields']['name'],
        'rankings': [float(entry['fields']['rating_factor_%d' % idx])
                     for idx in xrange(1, 4)],
        'timezone': u'UTC%s%d' % (
                         u'' if entry['fields']['timezone'] < 0 else u'+',
                         entry['fields']['timezone']),
        'total_ranking': float(entry['fields']['total_rating']),
        'coordinates': [float(entry['fields']['latitude']),
                        float(entry['fields']['longitude'])],
        'country': Country.find_one({
                         'old_pk': entry['fields']['country']})._id,
    }
    additional_corresp_map = {
        'old_pk': entry['pk'],
    }
    city = City.find_one({'old_pk': entry['pk']})
    if not city:
        city = City()

    city.set_lang("en")
    for k, v in corresp_map.iteritems():
        setattr(city, k, v)

    for k, v in additional_corresp_map.iteritems():
        city[k] = v

    city.save()

    return city


def post_migrate():
    """
    Post-migration phase: index generations, cross-document relationships.
    """
    for country in Country.find():
        country['capital_city'] = City.find_one({
                      'old_pk': country['old_capitalcity_pk']})._id

        del country['old_capitalcity_pk']
        country.save()

    for cls in (City, Country, Region):
        cls.generate_index(cls.collection)


def main(args):
    """
    Main function, entry point of the script.
    """
    orig_file = '/tmp/migrate_dump.json'
    if args.path.endswith(('.bzip2', '.bz2')):
        orig_file_zipped = '/tmp/migrate_dump.json.bz2'
        shutil.copy(args.path, orig_file_zipped)
        os.spawnlp(os.P_WAIT, 'bunzip2', 'bunzip2', orig_file_zipped)
    elif args.path.endswith(('.gz', '.gzip')):
        orig_file_zipped = '/tmp/migrate_dump.json.gz'
        shutil.copy(args.path, orig_file_zipped)
        os.spawnlp(os.P_WAIT, 'gunzip', 'gunzip', orig_file_zipped)
    else:
        orig_file = args.path

    with open(orig_file, "r") as fh:
        json_resp = json.load(fh)
        for this_entry in json_resp:
            if this_entry['model'] == 'triplander.country':
                migrate_country(this_entry)
            elif this_entry['model'] == 'triplander.city':
                migrate_city(this_entry)

    post_migrate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                 description='Migrates a PostgreSQL JSON to MongoDB style.')
    parser.add_argument("path", help="An alternate path to the JSON file",
                        default=FILE_PATH, nargs='?')

    args = parser.parse_args()
    main(args)
    sys.exit(0)  # successful termination
