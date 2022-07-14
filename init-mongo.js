var db=connect("mongodb://root:password@192.168.1.4:27017/")
db=db.getSiblingDB('demo_db')

db.createUser(
    {
        user:"root",
        pwd:"password",
        roles:[
            {
                role:"readWrite",
                db:"demo_db"
            }
        ]
    }
)