Some climbing related apps and tooling I've been building for my home wall. This includes;

### A boulder tracking app
I've used a segment-anything derivitive in order to identify climbings holds. This
makes it easier to tinker with my wall, while keeping my climbs and making it quick to add hold configuration changes.

### A load sensor app
Not much here just yet

## Getting Started

populate .env files (see .env.template files)
git clone https://github.com/IDEA-Research/GroundingDINO.git
git clone https://github.com/luca-medeiros/lang-segment-anything.git
docker-compose up --build

## Deployment

Long-term state is stored on S3 and MongoDB. You'll need something to provide for those interfaces and populate backend/.env

