# Ovitrap Egg Counter - Server app

## Suggestions
- [ ] capture -> record
- [ ] app compartiments for different regions 
- [ ] record model: add user, country, postal code 

## Remarks
- Deploying on Heroku with Conda: needed to install pip through conda then "pip list --format=freeze > requirements.txt"
- Heroku's free PostreSQL plan: 10k rows, 1GB max
- Maintenance mode can be enabled: $ heroku maintenance:on
- u40725 / tosquimos5050
- client-app / oeg-pass-not-secure: can only view and add captures
- should allow to flag captures for deletion
- S3 bucket: objects are currently public. should edit CORS policy to include only this app's domain name
- Netlify and Heroku are great
