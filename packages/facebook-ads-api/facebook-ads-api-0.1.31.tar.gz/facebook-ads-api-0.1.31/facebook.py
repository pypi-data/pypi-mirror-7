import codecs
import datetime
import hashlib
import hmac
import io
import json
import logging
import mimetypes
import sys
import urllib
import urllib2
import uuid

FACEBOOK_API = 'https://graph.facebook.com'

logger = logging.getLogger(__name__)


class MultipartFormdataEncoder(object):
    def __init__(self):
        self.boundary = uuid.uuid4().hex
        self.content_type = 'multipart/form-data; boundary={}'.format(
            self.boundary)

    @classmethod
    def u(cls, s):
        if sys.hexversion < 0x03000000 and isinstance(s, str):
            s = s.decode('utf-8')
        if sys.hexversion >= 0x03000000 and isinstance(s, bytes):
            s = s.decode('utf-8')
        return s

    def iter(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, file-like) elements for data
        to be uploaded as files.
        Yield body's chunk as bytes
        """
        encoder = codecs.getencoder('utf-8')
        for key, value in fields.iteritems():
            key = self.u(key)
            yield encoder('--{}\r\n'.format(self.boundary))
            yield encoder(self.u(
                'Content-Disposition: form-data; name="{}"\r\n').format(key))
            yield encoder('\r\n')
            if isinstance(value, int) or isinstance(value, float):
                value = str(value)
            yield encoder(self.u(value))
            yield encoder('\r\n')
        for key, value in files.iteritems():
            key = self.u(key)
            filename = self.u(value.name)
            yield encoder('--{}\r\n'.format(self.boundary))
            yield encoder(self.u('Content-Disposition: form-data; name="{}"; filename="{}"\r\n').format(key, filename))
            yield encoder('Content-Type: {}\r\n'.format(mimetypes.guess_type(filename)[0] or 'application/octet-stream'))
            yield encoder('\r\n')
            buff = value.read()
            yield (buff, len(buff))
            yield encoder('\r\n')
        yield encoder('--{}--\r\b'.format(self.boundary))

    def encode(self, fields, files):
        body = io.BytesIO()
        for chunk, chunk_len in self.iter(fields, files):
            body.write(chunk)
        return self.content_type, body.getvalue()


class AdsAPIError(Exception):
    """
    Errors as defined in the Facebook documentation
    https://developers.facebook.com/docs/reference/ads-api/error-reference/
    """
    def __init__(self, error):
        data = json.load(error)
        self.error = data
        self.message = data['error']['message']
        self.code = data['error']['code']
        self.type = data['error']['type']

    def __str__(self):
        return '(%s %s) %s' % (self.type, self.code, self.message)


class AdsAPI(object):
    """A client for the Facebook Ads API."""
    DATA_LIMIT = 100

    def __init__(self, access_token, app_id, app_secret):
        self.access_token = access_token
        self.app_id = app_id
        self.app_secret = app_secret
        h = hmac.new(access_token, app_secret, hashlib.sha256)
        self.appsecret_proof = h.hexdigest()

    def make_request(self, path, method, args=None, files=None, batch=False):
        """Makes a request against the Facebook Ads API endpoint."""
        args = dict(args or {})

        if batch:
            # Then just return a dict for the batch request
            return {
                'method': method,
                'relative_url': '%s?%s' % (path, urllib.urlencode(args))
            }
        logger.info('Making a %s request at %s with %s' % (method, path, args))
        if 'access_token' not in args:
            args['access_token'] = self.access_token
        try:
            if method == 'GET':
                url = '%s/%s?%s' % (FACEBOOK_API, path, urllib.urlencode(args))
                f = urllib2.urlopen(url)
            elif method == 'POST':
                url = '%s/%s' % (FACEBOOK_API, path)
                if files:
                    encoder = MultipartFormdataEncoder()
                    content_type, body = encoder.encode(args, files)
                    req = urllib2.Request(url, data=body)
                    req.add_header('Content-Type', content_type)
                    f = urllib2.urlopen(req)
                else:
                    f = urllib2.urlopen(url, urllib.urlencode(args))
            elif method == 'DELETE':
                url = '%s/%s?%s' % (FACEBOOK_API, path, urllib.urlencode(args))
                req = urllib2.Request(url)
                req.get_method = lambda: 'DELETE'
                f = urllib2.urlopen(req)
            else:
                raise
            return json.load(f)
        except urllib2.HTTPError as e:
            print '%s' % e
            raise AdsAPIError(e)
        except urllib2.URLError as e:
            print 'URLError: %s' % e.reason

    def make_batch_request(self, batch):
        """Makes a batched request against the Facebook Ads API endpoint."""
        args = {}
        args['access_token'] = self.access_token
        args['batch'] = json.dumps(batch)
        logger.info('Making a batched request with %s' % args)
        try:
            f = urllib2.urlopen(FACEBOOK_API, urllib.urlencode(args))
            data = json.load(f)
            # For debugging
            self.data = data
            for idx, val in enumerate(data):
                data[idx] = json.loads(val['body'])
            return data
        except urllib2.HTTPError as e:
            print '%s' % e
            return json.load(e)
        except urllib2.URLError as e:
            print 'URLError: %s' % e.reason

    # New API
    def make_labeled_batch_request(self, batch):
        """Makes a batched request with label against the Facebook Ads API endpoint."""
        try:
            labels = batch.keys()
            queries = batch.values()
            data = self.make_batch_request(queries)
            # For debugging
            self.data = data
            return dict(zip(labels, data))
        except urllib2.HTTPError as e:
            print '%s' % e
            return json.load(e)
        except urllib2.URLError as e:
            print 'URLError: %s' % e.reason

    def debug_token(self, token):
        """Returns debug information about the given token."""
        path = 'debug_token'
        args = {
            'input_token': token,
            'access_token': '%s|%s' % (self.app_id, self.app_secret)
        }
        return self.make_request(path, 'GET', args)

    def get_adusers(self, account_id, batch=False):
        """Returns the users of the given ad account."""
        path = 'act_%s/users' % account_id
        return self.make_request(path, 'GET', batch=batch)

    def get_adaccount(self, account_id, fields=None, batch=False):
        """Returns the fields of the given ad account."""
        path = 'act_%s' % account_id
        args = {'fields': fields} if fields else {}
        return self.make_request(path, 'GET', args, batch=batch)

    def get_adaccounts(self, user_id, fields, batch=False):
        """Returns the list of Facebook ad accounts."""
        path = '%s/adaccounts' % user_id
        args = {'fields': fields}
        return self.make_request(path, 'GET', args, batch=batch)

    # New API
    def get_adcampaign_group(self, campaign_group_id, fields, batch=False):
        """Return the fields for the given ad campaign group."""
        path = '%s' % campaign_group_id
        args = {'fields': fields}
        return self.make_request(path, 'GET', args, batch=batch)

    # New API
    def get_adcampaign_groups(self, account_id, fields, batch=False):
        """Returns the fields of all ad campaign groups from the given ad account."""
        path = 'act_%s/adcampaign_groups' % account_id
        args = {
            'fields': fields,
            'limit': self.DATA_LIMIT
        }
        return self.make_request(path, 'GET', args, batch=batch)

    # New API
    def delete_adcampaign_group(self, campaign_group_id, batch=False):
        """Delete specific campaign group."""
        path = '%s' % campaign_group_id
        return self.make_request(path, 'DELETE', batch=batch)

    def get_adcampaign(self, campaign_id, fields, batch=False):
        """Returns the fields for the given ad campaign."""
        path = '%s' % campaign_id
        args = {'fields': fields}
        return self.make_request(path, 'GET', args, batch=batch)

    # New API
    def get_adcampaigns_of_campaign_group(self, campaign_group_id, fields, batch=False):
        """Return the fields of all adcampaigns from the given adcampaign group."""
        path = '%s/adcampaigns' % campaign_group_id
        args = {'fields': fields}
        return self.make_request(path, 'GET', args, batch=batch)

    # New API
    def get_adcampaigns_of_account(self, account_id, fields, batch=False):
        """Returns the fields of all ad sets from the given ad account."""
        path = 'act_%s/adcampaigns' % account_id
        args = {'fields': fields}
        return self.make_request(path, 'GET', args, batch=batch)

    def get_adcampaigns(self, account_id, fields=None, batch=False):
        """Returns the fields of all ad sets from the given ad account."""
        return self.get_adcampaigns_of_account(account_id, fields, batch=batch)

    def get_adgroup(self, adgroup_id, fields=None, batch=False):
        """Returns the fields for the given ad group."""
        path = '%s' % adgroup_id
        args = {'fields': fields} if fields else {}
        return self.make_request(path, 'GET', args, batch=batch)

    def get_adgroups_by_adaccount(self, account_id, fields=None, batch=False):
        """Returns the fields of all ad groups from the given ad account."""
        path = 'act_%s/adgroups' % account_id
        args = {'fields': fields} if fields else {}
        return self.make_request(path, 'GET', args, batch=batch)

    def get_adgroups_by_adcampaign(self, campaign_id, fields=None, batch=False):
        """Returns the fields of all ad groups from the given ad campaign."""
        path = '%s/adgroups' % campaign_id
        args = {'fields': fields} if fields else {}
        return self.make_request(path, 'GET', args, batch=batch)

    def get_adcreative(self, creative_id, fields, batch=False):
        """Returns the fields for the given ad creative."""
        path = '%s' % creative_id
        args = {'fields': fields}
        return self.make_request(path, 'GET', args, batch=batch)

    def get_adcreatives(self, account_id, fields, batch=False):
        """Returns the fields for the given ad creative."""
        path = 'act_%s/adcreatives' % account_id
        args = {'fields': fields}
        return self.make_request(path, 'GET', args, batch=batch)

    def get_adimages(self, account_id, hashes=None, batch=False):
        """Returns the ad images for the given ad account."""
        path = 'act_%s/adimages' % account_id
        args = {}
        if hashes is not None:
            args = {'hashes': hashes}
        return self.make_request(path, 'GET', args, batch=batch)

    def get_stats_by_adaccount(self, account_id, batch=False):
        """Returns the stats for a Facebook campaign."""
        path = 'act_%s/adcampaignstats' % account_id
        return self.make_request(path, 'GET', batch=batch)

    # New API
    def get_stats_by_adcampaign_group(
            self, campaign_group_id, fields=None, filters=None, batch=False):
        """Returns the stats for a Facebook campaign group."""
        path = '%s/stats' % campaign_group_id
        args = {}
        if fields:
            args['fields'] = json.dumps(fields)
        if filters:
            args['filters'] = json.dumps(filters)
        return self.make_request(path, 'GET', args, batch=batch)

    def get_stats_by_adcampaign(self, account_id, campaign_ids=None,
                                batch=False):
        """Returns the stats for a Facebook campaign by adcampaign."""
        path = 'act_%s/adcampaignstats' % account_id
        args = {}
        if campaign_ids is not None:
            args['campaign_ids'] = json.dumps(campaign_ids)
        return self.make_request(path, 'GET', args, batch=batch)

    def get_stats_by_adgroup(self, account_id, adgroup_ids=None, batch=False):
        """Returns the stats for a Facebook campaign by adgroup."""
        path = 'act_%s/adgroupstats' % account_id
        args = {}
        if adgroup_ids is not None:
            args['adgroup_ids'] = json.dumps(adgroup_ids)
        return self.make_request(path, 'GET', args, batch=batch)

    # New API
    def get_time_interval(self, start, end):
        """Returns formatted time interval."""
        if not start or not end:
            return None
        end = end + datetime.timedelta(1)
        if not isinstance(start, datetime.datetime):
            start = datetime.datetime(start)
        if not isinstance(end, datetime.datetime):
            end = datetime.datetime(end)
        time_interval = dict(
            day_start=dict(day=start.day, month=start.month, year=start.year),
            day_stop=dict(day=end.day, month=end.month, year=end.year)
        )
        return json.dumps(time_interval)

    def get_adreport_stats(self, account_id, date_preset, time_increment,
                           data_columns, filters=None, actions_group_by=None,
                           batch=False):
        """Returns the ad report stats for the given account."""
        path = 'act_%s/reportstats' % account_id
        args = {
            'date_preset': date_preset,
            'time_increment': time_increment,
            'data_columns': json.dumps(data_columns),
        }
        if filters is not None:
            args['filters'] = json.dumps(filters)
        if actions_group_by is not None:
            args['actions_group_by'] = actions_group_by
        return self.make_request(path, 'GET', args, batch=batch)

    # New API
    def get_adreport_stats2(self, account_id, data_columns, date_preset=None,
                            date_start=None, date_end=None, time_increment=None,
                            actions_group_by=None, filters=None, async=False,
                            batch=False):
        """Returns the ad report stats for the given account."""
        if date_preset is None and date_start is None and date_end is None:
            raise BaseException("Either a date_preset or a date_start/end must be set when requesting a stats info.")
        path = 'act_%s/reportstats' % account_id
        args = {
            'data_columns': json.dumps(data_columns),
        }
        if date_preset:
            args['date_preset'] = date_preset
        if date_start and date_end:
            args['time_interval'] = \
                self.get_time_interval(date_start, date_end)
        if time_increment:
            args['time_increment'] = time_increment
        if filters:
            args['filters'] = json.dumps(filters)
        if actions_group_by:
            args['actions_group_by'] = actions_group_by
        if async:
            args['async'] = 'true'
            return self.make_request(path, 'POST', args=args, batch=batch)
        return self.make_request(path, 'GET', args=args, batch=batch)

    # New API
    def get_async_job_status(self, job_id, batch=False):
        """Returns the asynchronously requested job status"""
        path = '%s' % job_id
        return self.make_request(path, 'GET', batch=batch)

    # New API
    def get_async_job_result(self, account_id, job_id, batch=False):
        """Returns completed result of the given async job"""
        path = 'act_%s/reportstats' % account_id
        args = {
            'report_run_id': job_id
        }
        return self.make_request(path, 'GET', args=args, batch=batch)

    def get_conversion_stats_by_adaccount(self, account_id, batch=False):
        """Returns the aggregated conversion stats for the given ad account."""
        path = 'act_%s/conversions' % account_id
        return self.make_request(path, 'GET', batch=batch)

    def get_conversion_stats_by_adcampaign(self, account_id, campaign_ids=None,
                                           include_deleted=False, batch=False):
        """Returns the conversions stats for all ad campaigns."""
        path = 'act_%s/adcampaignconversions' % account_id
        args = {}
        if campaign_ids is not None:
            args['campaign_ids'] = json.dumps(campaign_ids)
        if include_deleted is not None:
            args['include_deleted'] = include_deleted
        return self.make_request(path, 'GET', args, batch=batch)

    def get_conversion_stats_by_adgroup(self, account_id, adgroup_ids=None,
                                        include_deleted=False, batch=False):
        """Returns the conversions stats for all ad groups."""
        path = 'act_%s/adgroupconversions' % account_id
        args = {}
        if adgroup_ids is not None:
            args['adgroup_ids'] = json.dumps(adgroup_ids)
        if include_deleted is not None:
            args['include_deleted'] = include_deleted
        return self.make_request(path, 'GET', args, batch=batch)

    def get_conversion_stats(self, adgroup_id, batch=False):
        """Returns the conversion stats for a single ad group."""
        path = '%s/conversions' % adgroup_id
        return self.make_request(path, 'GET', batch=batch)

    def get_offsite_pixel(self, offsite_pixel_id, batch=False):
        """Returns the information for the given offsite pixel."""
        path = '%s' % offsite_pixel_id
        return self.make_request(path, 'GET', batch=batch)

    def get_offsite_pixels(self, account_id, batch=False):
        """Returns the list of offsite pixels for the given account."""
        path = 'act_%s/offsitepixels' % account_id
        return self.make_request(path, 'GET', batch=batch)

    def get_keyword_stats(self, adgroup_id, batch=False):
        """Returns the keyword stats for the given ad group."""
        path = '%s/keywordstats' % adgroup_id
        return self.make_request(path, 'GET', batch=batch)

    def get_ratecard(self, account_id, batch=False):
        """Returns the rate card for Homepage Ads."""
        path = 'act_%s/ratecard' % account_id
        return self.make_request(path, 'GET', batch=batch)

    def get_reach_estimate(self, account_id, currency, targeting_spec,
                           creative_action_spec=None,
                           bid_for=None, batch=False):
        """Returns the reach estimate for the given currency and targeting."""
        path = 'act_%s/reachestimate' % account_id
        args = {
            'currency': currency,
            'targeting_spec': targeting_spec,
        }
        if creative_action_spec is not None:
            args['creative_action_spec'] = creative_action_spec
        if bid_for is not None:
            args['bid_for'] = bid_for
        return self.make_request(path, 'GET', args, batch=batch)

    def get_adcampaign_list(self, account_id):
        """Returns the list of ad campaigns and related data."""
        fields = 'id, name, campaign_status, start_time, end_time, ' \
                 'daily_budget, lifetime_budget, budget_remaining'
        batch = [
            self.get_adaccount(account_id, ['currency'], batch=True),
            self.get_adcampaigns(account_id, fields, batch=True),
            self.get_stats_by_adcampaign(account_id, batch=True),
        ]
        return self.make_batch_request(batch)

    def get_adcampaign_detail(self, account_id, campaign_id, date_preset):
        """Returns the detail of an ad campaign."""
        campaign_fields = [
            'name', 'campaign_status', 'daily_budget', 'lifetime_budget',
            'start_time', 'end_time']
        campaign_data_columns = [
            'campaign_name', 'reach', 'frequency', 'clicks',
            'actions', 'total_actions', 'ctr', 'spend']
        adgroup_data_columns = [
            'campaign_id', 'campaign_name', 'adgroup_id', 'adgroup_name',
            'reach', 'frequency', 'clicks', 'ctr', 'actions', 'cpm', 'cpc',
            'spend']
        demographic_data_columns = [
            'campaign_id', 'reach', 'frequency', 'clicks', 'actions', 'spend',
            'cpc', 'cpm', 'ctr', 'cost_per_total_action', 'age', 'gender']
        placement_data_columns = [
            'campaign_id', 'reach', 'frequency', 'clicks', 'actions', 'spend',
            'cpc', 'cpm', 'ctr', 'cost_per_total_action', 'placement']
        campaign_filters = [{
            'field': 'campaign_id', 'type': 'in', 'value': [campaign_id]}]
        batch = [
            self.get_adaccount(account_id, ['currency'], batch=True),
            self.get_adcampaign(campaign_id, campaign_fields, batch=True),
            self.get_adreport_stats(
                account_id, date_preset, 'all_days', campaign_data_columns,
                campaign_filters, ['action_type'], True),
            self.get_adreport_stats(
                account_id, date_preset, 1, campaign_data_columns,
                campaign_filters, None, True),
            self.get_adreport_stats(
                account_id, date_preset, 'all_days', adgroup_data_columns,
                campaign_filters, None, True),
            self.get_adreport_stats(
                account_id, date_preset, 'all_days', demographic_data_columns,
                campaign_filters, None, True),
            self.get_adreport_stats(
                account_id, date_preset, 'all_days', placement_data_columns,
                campaign_filters, None, True),
        ]
        return self.make_batch_request(batch)

    def get_user_pages(self, user_id, fields=None, batch=False):
        """Returns the list of pages to which user has access with tokens."""
        path = '%s/accounts' % user_id
        args = {}
        if fields:
            args['fields'] = json.dumps(fields)
        return self.make_request(path, 'GET', args, batch=batch)

    def get_autocomplete_data(self, q, type, want_localized_name=False,
                              list=None, limit=None, batch=False):
        """Returns the autocomplete data for the given query and type."""
        path = '%s/search' % q
        args = {'type': type}
        if want_localized_name:
            args['want_localized_name'] = want_localized_name
        if list:
            args['list'] = list
        if limit:
            args['limit'] = limit
        return self.make_request(path, 'GET', args, batch=batch)

    def get_page_access_token(self, page_id, batch=False):
        """Returns the page access token for the given page."""
        path = '%s' % page_id
        args = {'fields': 'access_token'}
        return self.make_request(path, 'GET', args, batch=batch)

    def create_link_page_post(self, page_id, link, message=None, picture=None,
                              thumbnail=None, name=None, caption=None,
                              description=None, published=None, batch=False):
        """Creates a link page post on the given page."""
        # TODO: this method is calling the API twice; combine them into batch
        page_access_token = self.get_page_access_token(page_id)
        path = '%s/feed' % page_id
        args = {
            'link': link,
            'access_token': page_access_token['access_token'],
        }
        files = {}
        if message is not None:
            args['message'] = message
        if picture is not None:
            args['picture'] = picture
        if thumbnail is not None:
            files['thumbnail'] = thumbnail
        if published is not None:
            args['published'] = published
        if name is not None:
            args['name'] = name
        if caption is not None:
            args['caption'] = caption
        if description is not None:
            args['description'] = description
        return self.make_request(path, 'POST', args, files, batch=batch)

    def create_video_page_post(self, page_id, source, title=None,
                               description=None, thumb=None, published=True,
                               scheduled_publish_time=None, batch=False):
        # TODO: this method is calling the API twice; combine them into batch
        page_access_token = self.get_page_access_token(page_id)
        path = '%s/videos' % page_id
        args = {
            'published': published,
            'access_token': page_access_token['access_token'],
        }
        files = {'source': source}
        if title is not None:
            args['title'] = title
        if description is not None:
            args['description'] = description
        if thumb is not None:
            files['thumb'] = thumb
        if scheduled_publish_time is not None:
            args['scheduled_publish_time'] = scheduled_publish_time
        return self.make_request(path, 'POST', args, files, batch=batch)

    # New API
    def create_adcampaign_group(self, account_id, name, campaign_group_status,
                                objective=None, batch=False):
        """Creates an ad campaign group for the given account."""
        path = 'act_%s/adcampaign_groups' % account_id
        args = {
            'name': name,
            'campaign_group_status': campaign_group_status,
        }
        if objective is not None:
            args['objective'] = objective
        return self.make_request(path, 'POST', args, batch=batch)

    # New API
    def update_adcampaign_group(self, campaign_group_id, name=None,
                                campaign_group_status=None, objective=None,
                                batch=False):
        """Updates condition of the given ad campaign group."""
        path = '%s' % campaign_group_id
        args = {}
        if name is not None:
            args['name'] = name
        if campaign_group_status is not None:
            args['campaign_group_status'] = campaign_group_status
        if objective is not None:
            args['objective'] = objective
        return self.make_request(path, 'POST', args, batch=batch)

    # New API: Need to change 'create_adcampaign' when facebook api is set new api.
    def _create_adcampaign(self, account_id, campaign_group_id, name,
                           campaign_status,
                           daily_budget=None, lifetime_budget=None,
                           start_time=None, end_time=None, batch=False):
        """Creates an ad campaign for the given account."""
        if daily_budget is None and lifetime_budget is None:
            raise BaseException("Either a lifetime_budget or a daily_budget must be set when creating a campaign")
        if lifetime_budget is not None and end_time is None:
            raise BaseException("end_time is required when lifetime_budget is specified")
        path = 'act_%s/adcampaigns' % account_id
        args = {
            'campaign_group_id': campaign_group_id,
            'name': name,
            'campaign_status': campaign_status,
        }
        if daily_budget:
            args['daily_budget'] = daily_budget
        if lifetime_budget:
            args['lifetime_budget'] = lifetime_budget
        if start_time:
            args['start_time'] = start_time
        if end_time:
            args['end_time'] = end_time
        return self.make_request(path, 'POST', args, batch=batch)

    # Deprecated: this method will be update.
    def create_adcampaign(self, account_id, name, campaign_status,
                          daily_budget=None, lifetime_budget=None,
                          start_time=None, end_time=None, batch=False):
        """Creates an ad campaign for the given account."""
        if daily_budget is None and lifetime_budget is None:
            raise BaseException("Either a lifetime_budget or a daily_budget must be set when creating a campaign")
        if lifetime_budget is not None and end_time is None:
            raise BaseException("end_time is required when lifetime_budget is specified")
        path = 'act_%s/adcampaigns' % account_id
        args = {
            'name': name,
            'campaign_status': campaign_status,
        }
        if daily_budget:
            args['daily_budget'] = daily_budget
        if lifetime_budget:
            args['lifetime_budget'] = lifetime_budget
        if start_time:
            args['start_time'] = start_time
        if end_time:
            args['end_time'] = end_time
        return self.make_request(path, 'POST', args, batch=batch)

    # New API
    def update_adcampaign(self, campaign_id, name=None, campaign_status=None,
                          daily_budget=None, lifetime_budget=None,
                          end_time=None, batch=False):
        """Updates condition of the given ad campaign."""
        path = '%s' % campaign_id
        args = {}
        if name:
            args['name'] = name
        if campaign_status:
            args['campaign_status'] = campaign_status
        if daily_budget:
            args['daily_budget'] = daily_budget
        if lifetime_budget:
            args['lifetime_budget'] = lifetime_budget
        if end_time:
            args['end_time'] = end_time
        return self.make_request(path, 'POST', args, batch=batch)

    # New API
    def delete_adcampaign(self, campaign_id, batch=False):
        """Delete the given ad campaign."""
        path = '%s' % campaign_id
        return self.make_request(path, 'DELETE', batch=batch)

    def create_adcreative_type_27(self, account_id, object_id,
                                  auto_update=None, story_id=None,
                                  url_tags=None, name=None, batch=False):
        """Creates an ad creative in the given ad account."""
        path = 'act_%s/adcreatives' % account_id
        args = {
            'type': 27,
            'object_id': object_id,
        }
        if auto_update:
            args['auto_update'] = auto_update
        if story_id:
            args['story_id'] = story_id
        if url_tags:
            args['url_tags'] = url_tags
        if name:
            args['name'] = name
        return self.make_request(path, 'POST', args, batch=batch)

    def create_adgroup(self, account_id, name, bid_type, bid_info, campaign_id,
                       creative_id, targeting, conversion_specs=None,
                       tracking_specs=None, view_tags=None, objective=None,
                       batch=False):
        """Creates an adgroup in the given ad camapaign with the given spec."""
        path = 'act_%s/adgroups' % account_id
        args = {
            'name': name,
            'bid_type': bid_type,
            'bid_info': json.dumps(bid_info),
            'campaign_id': campaign_id,
            'creative': json.dumps({'creative_id': creative_id}),
            'targeting': json.dumps(targeting),
        }
        if conversion_specs:
            args['conversion_specs'] = json.dumps(conversion_specs)
        if tracking_specs:
            args['tracking_specs'] = json.dumps(tracking_specs)
        if view_tags:
            args['view_tags'] = json.dumps(view_tags)
        if objective:
            args['objective'] = objective
        return self.make_request(path, 'POST', args, batch=batch)

    def update_adgroup(self, adgroup_id, name=None, bid_type=None, bid_info=None,
                       creative_id=None, targeting=None, conversion_specs=None,
                       tracking_specs=None, view_tags=None, objective=None,
                       batch=False):
        """Updates condition of the given ad group."""
        path = "%s" % adgroup_id
        args = {}
        if name:
            args['name'] = name
        if bid_type:
            args['bid_type'] = bid_type
        if bid_info:
            args['bid_info'] = json.dumps(bid_info)
        if creative_id:
            args['creative'] = json.dumps({'creative_id': creative_id})
        if targeting:
            args['targeting'] = json.dumps(targeting)
        if conversion_specs:
            args['conversion_specs'] = json.dumps(conversion_specs)
        if tracking_specs:
            args['tracking_specs'] = json.dumps(tracking_specs)
        if view_tags:
            args['view_tags'] = json.dumps(view_tags)
        if objective:
            args['objective'] = objective
        return self.make_request(path, 'POST', args, batch=batch)

    def create_offsite_pixel(self, account_id, name, tag, batch=False):
        """Creates an offsite pixel for the given account."""
        path = 'act_%s/offsitepixels' % account_id
        args = {
            'name': name,
            'tag': tag,
        }
        return self.make_request(path, 'POST', args, batch=batch)
