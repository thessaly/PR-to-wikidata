from app import app
from flask import Flask, request, jsonify
import pywikibot
import os
from github import Github
import base64
import hashlib
import hmac
import json
import csv
from dotenv import load_dotenv
# import StringIO


load_dotenv()


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['success'] = False
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/payload', methods=['POST'])
def parse_request():
    event = request.headers.get('X-GitHub-Event')
    gh_sig = request.headers.get('X-Hub-Signature')
    data = request.json

    print(request.headers)

    # if not validate_signature(request.get_data(), gh_sig):
    #    raise InvalidUsage('Wrong secret', status_code=401)

    if event != 'push':
        raise InvalidUsage('Invalid event, failed successfully :)', status_code=400)

    file_of_push = []
    file_of_push.extend(data['head_commit'].get('added', []))
    file_of_push.extend(data['head_commit'].get('modified', []))

    filename = 'test.csv'
    if filename in file_of_push:
        g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))
        repo = g.get_repo(data['repository']['full_name'])
        goshmap = repo.get_contents(filename)
        content = base64.b64decode(goshmap.content)
        update_wikidata(content)
        # new_content = update_wikidata(content)
        # path = goshmap.path
        # sha = goshmap.sha
        # repo.update_file(path, 'Update with new Q-ID', new_content, sha)
        return jsonify({'success': True})
    else:
        return jsonify({'success': True, 'message': 'No relevant file in push'})

def update_wikidata(data):
    # site = pywikibot.Site("wikidata", "wikidata")
    site = pywikibot.Site("test", "wikidata")
    repo = site.data_repository()

    decoded_data = data.decode('utf-8')
    #decoded_data = data
    reader = csv.DictReader(decoded_data.splitlines())
    rows = []
    for row in reader:
        row_dict = dict(row)
        rows.append(row_dict)

    # Loop over CSV file
    output_rows = []
    for row in rows[-1:]:
        try:
            new_id = create_gosh_claims(site, repo, row)
            if new_id:
                row['item'] = new_id
            output_rows.append(row)
        except pywikibot.data.api.APIError as e:
            print("API Error: %s" % (e))
        continue
    # output = StringIO.StringIO()
    # fieldnames = rows[0].keys()
    # writer = csv.DictWriter(output, fieldnames=fieldnames)

    # writer.writeheader()
    # for out_row in output_rows:
    #     writer.writerow(out_row)
    # content = output.getvalue()
    # output.close()
    # return content

def validate_signature(payload, gh_sig):
    secret = os.getenv('GITHUB_WEBHOOK_SECRET')
    signature = hmac.new(
        str(secret),
        str(payload),
        hashlib.sha1
    ).hexdigest()

    return hmac.compare_digest(signature, gh_sig.split('=')[1])

def create_gosh_claims(site, repo, row):
    print()
    print("Add new value: %s" % row)
    
    # row['item'] = sandbox_item
    
    new_id = None
    if row['item']:
        print("There is already a Q-ID: %s, skipping" % row['item'])
        return
        #wd_item = pywikibot.ItemPage(repo, row['item'])
    else:
        # create a new item
        wd_item = pywikibot.ItemPage(site)
        labels = {"en": row['itemLabel']}
        wd_item.editLabels(labels=labels, summary="Setting labels")
        new_id = wd_item.getID()
    
    #uses_prop_id = 'P2283'
    #location_prop = 'P276'
    #website_prop = 'P856'
    #field_of_work_prop = 'P101'
    #part_of_prop = 'P361'
    #url_prop_id = 'P854'
    uses_prop_id = 'P95225'
    location_prop = 'P286'
    website_prop = 'P206'
    field_of_work_prop = 'P85468'
    part_of_prop = 'P791'
    url_prop_id = 'P93'
    
    # source
    source_url = 'https://github.com/thessaly/phd'
    
    # 1. open science hardware claim
    #open_science_hardware = pywikibot.ItemPage(repo, "Q62392060")
    source = pywikibot.Claim(repo, url_prop_id)
    source.setTarget(source_url)
    open_science_hardware = pywikibot.ItemPage(repo, "Q210959")
    osh_claim = pywikibot.Claim(repo, uses_prop_id)
    osh_claim.setTarget(open_science_hardware)
    osh_claim.addSource(source)
    wd_item.addClaim(osh_claim, summary="Add Open Science Hardware claim to %s" % wd_item.getID())
    print("Added Open Science Hardware claim to %s" % wd_item.getID())
    
    # 2. Location
    # We try to match this to a city, otherwise we save the coordinates
    source = pywikibot.Claim(repo, url_prop_id)
    source.setTarget(source_url)
    
    # 3. Official website/repository
    source = pywikibot.Claim(repo, url_prop_id)
    source.setTarget(source_url)
    website_claim = pywikibot.Claim(repo, website_prop)
    website = row['url']
    if not website.startswith('http'):
        website = 'https://%s' % website
    website_claim.setTarget(website)
    website_claim.addSource(source)
    wd_item.addClaim(website_claim, summary="Add official website claim to %s" % wd_item.getID())
    print("Added website claim to %s" % wd_item.getID())
    
    # 4. Field of work of the initiative
    #field_of_work_mapping = {
    #    'education': 'Q8434',
    #    'art': 'Q735',
    #    'academic research': 'Q62393045',
    #    'community science': 'Q62392920',
    #}
    source = pywikibot.Claim(repo, url_prop_id)
    source.setTarget(source_url)
    field_of_work_mapping = {
        'Education': 'Q40741',
        'Art': 'Q210966',
        'Academic research': 'Q210967',
        'Community Science': 'Q210968',
        'Social innovation': 'Q210987',
    }
    if row['areaLabel'] in field_of_work_mapping:
        area = pywikibot.ItemPage(repo, field_of_work_mapping[row['areaLabel']])
        fow_claim = pywikibot.Claim(repo, field_of_work_prop)
        fow_claim.setTarget(area)
        fow_claim.addSource(source)
        wd_item.addClaim(fow_claim, summary="Add field of work claim to %s" % wd_item.getID())
        print("Added field of work claim to %s" % wd_item.getID())
    else:
        print("Couldn't map field of work: %s" % row['areaLabel'])
    
    # 5. GOSH
    source = pywikibot.Claim(repo, url_prop_id)
    source.setTarget(source_url)
    if row['gosh'] == 'yes':
        #gosh = pywikibot.ItemPage(repo, "Q62391989")
        gosh = pywikibot.ItemPage(repo, "Q210969")
        gosh_claim = pywikibot.Claim(repo, part_of_prop)
        gosh_claim.setTarget(gosh)
        gosh_claim.addSource(source)
        wd_item.addClaim(gosh_claim, summary="Add part of gosh claim to %s" % wd_item.getID())
        print("Added gosh claim to %s" % wd_item.getID())
    else:
        print("Not part of GOSH")
    return new_id


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    port = os.getenv('PORT', 5000)
    print(port)
    app.run(threaded=True, port=port)
