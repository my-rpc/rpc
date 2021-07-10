formValidateErrors = function(response){
    ul = "<ul>";
    messages = response.responseJSON.message;
    for(var i in messages) {
        if(messages[i].length > 1 ){
            for(var j in messages[i]){
                ul += "<li>" + messages[i][j] + "</li>";
            }
        }else{
            ul += "<li>" + messages[i] + "</li>";
        }
    }
    ul += "</ul>";
    return ul;
};

toastInfo = function (message){
    $.toast({
        heading: 'Error',
        text: messages,
        position: 'top-right',
        loaderBg: '#ff6849',
        icon: 'info',
        hideAfter: 6000,
        stack: 6
    });
};

toastWarning  = function(message){
    $.toast({
        heading: 'Error',
        text: messages,
        position: 'top-right',
        loaderBg: '#ff6849',
        icon: 'warning',
        hideAfter: 6000,
        stack: 6
    });
};

toastError = function (message) { 
    console.log(message);
    $.toast({
        heading: 'Error',
        text: message,
        position: 'top-right',
        loaderBg: '#ff6849',
        icon: 'error',
        hideAfter: 6000,
        stack: 6
    });
};

toastSuccess = function (message){
    $.toast({
        heading: 'Error',
        text: messages,
        position: 'top-right',
        loaderBg: '#ff6849',
        icon: 'success',
        hideAfter: 6000,
        stack: 6
    });
    
};