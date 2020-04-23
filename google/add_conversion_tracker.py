#!/usr/bin/python

from googleads import adwords

client = adwords.AdWordsClient.LoadFromStorage()
conversion_tracker_service = client.GetService('ConversionTrackerService', version='v201609')

# Construct operations and add conversion_tracker.
operations = [
	{
		'operator': 'ADD',
		'operand': {
			'xsi_type': 'AdWordsConversionTracker',
			'name': 'TapQualityLeads1',
			'category': 'LEAD',
			'textFormat': 'HIDDEN',
			# Optional fields.
			'trackingCodeType': 'WEBSITE',
			'status': 'ENABLED',
			'viewthroughLookbackWindow': '15',
			'conversionPageLanguage': 'en',
			'backgroundColor': '#0000FF',
		}
	}
]
conversion_trackers = conversion_tracker_service.mutate(operations)

# Display results.
for conversion_tracker in conversion_trackers['value']:
	print ('Conversion tracker with id \'%s\', name \'%s\', status \'%s\' '
		'and category \'%s\' and snippet \n\'%s\'\n was added.\n' %
		(conversion_tracker['id'], conversion_tracker['name'],
			conversion_tracker['status'], conversion_tracker['category'],
			conversion_tracker['snippet']))
