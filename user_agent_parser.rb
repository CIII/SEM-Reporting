require 'device_detector'
require 'json'

user_agent = ARGV[0]
parser = DeviceDetector.new(user_agent)
browser_name = parser.name
browser_version = parser.full_version
os_name = parser.os_name
os_version = parser.os_full_version
is_bot = parser.bot?
bot_name = parser.bot_name
device_name = parser.device_name
device_type = parser.device_type
device_brand = parser.device_brand

data = [
	user_agent,
	browser_name,
	browser_version,
	os_name,
	os_version,
	is_bot,
	bot_name,
	device_name,
	device_type,
	device_brand
]

print JSON.generate(data)
