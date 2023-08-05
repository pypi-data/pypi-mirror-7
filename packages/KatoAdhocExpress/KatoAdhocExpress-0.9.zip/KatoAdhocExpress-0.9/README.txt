# KATO Adhoc Express

## Installation

	pip install kato-adhoc-express

## Usage

	from katoAdhocExpress import kato

	pkey = "<YOUR PUBLIC KEY>"

	skey = "<YOUR PRIVATE KEY>"
	
	
	exp = 3600
	
	user_id = '0'
	
	user_name = "John"	
	room_id = '0'

	room_name = "Kitchen"

	user_email= ''
	welcome_text= ''
	welcome_robot_name= ''

	url = kato.generateUrl(pkey, skey, exp, user_id, user_name, room_id, room_name, user_email, welcome_text, welcome_robot_name )

   

