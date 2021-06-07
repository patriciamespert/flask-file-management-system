console.log("hello world from flask!")


///////// USER LOGIN ///////////

usersArr = new Array();
let count = 0;


async function getUsers() {
    try{
        let res = await fetch(`${window.origin}/api/v1/users`)
        
        res.json().then(function(users) {

            console.log(users);

            let search = document.getElementById("email").value;

            getUser(users, search);

        
        })

    }catch(error){
        console.log(error)
    }
}

async function getUser(users, search) {

    try{


        for (const user of users){
        
            if (user.email == search){

                let res = await fetch(`${window.origin}/api/v1/user/${user.id}`)

                res.json().then(function(user) {

                    user_id = user[0]['stored_user_dict']['id'];

                    toDashboard(user_id);
                    
                })
            }
        }

    
    }catch(error){

        console.log(error)

    }

}

function toDashboard(user_id){
   
    fetch(`${window.origin}/api/v1/user/${user_id}`, {
            method: 'POST',
            headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json'
        },
            body: JSON.stringify
        })
            .then(function(response) {
                if (response.status !== 200) {
                    console.log(`Looks like there was a problem. Status code: ${response.status}`);
                    return;
                  }
                  response.json().then(function(data) {
                    
                    console.log(data);
                    console.log(data.data[0].admin_id);
                    console.log('files......');

                    if(data.data[0].admin_id == 0){
                        window.location.href = Flask.url_for('dashboard', {"email": data.data[0].email, "user_id": data.data[0].id});
                    }else{
                        window.location.href = Flask.url_for('admin_dashboard', {"email": data.data[0].email, "user_id": data.data[0].id});
                    }
             
                  });
            }).then(function(json) {
            
        });
    
}


document.onRefresh = function(event) {
    document.removeEventListener(event);
    console.log("refresh event removed");
}
