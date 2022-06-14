var selectElement = (s) => document.querySelector(s);

$("#navigation-panel").load("navbar.html", function(){        
    // open the menu on click
    selectElement('.open').addEventListener('click', () => {
        selectElement('.nav-list').classList.add('active');
    });
    // close the menu on click
    selectElement('.close').addEventListener('click', () => {
        selectElement('.nav-list').classList.remove('active');
    });

    $("#home-page").on('click', function(){
        $("#content-panel").load("home.html");
        selectActive("#home-page");
    });    

    $("#admin-page").on('click', function(){
        $("#content-panel").load("administration.html");
        selectActive("#admin-page");
    });

    $("#help-page").on('click', function(){
        $("#content-panel").load("help.html");
        selectActive("#help-page");
    });

    $("#contact-page").on('click', function(){
        $("#content-panel").load("contact.html");
        selectActive("#contact-page");
    });
     
});

function selectActive(removeFromTarget) {
    var item = selectElement('.current');
    selectElement(removeFromTarget).classList.add('current');
    selectElement(`#${item.id}`).classList.remove('current');
}

function doWork() {
    alert("button pressed");
}
