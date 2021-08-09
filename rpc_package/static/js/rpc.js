formValidateErrors = function(response){
    var ul = "<ul>";
    var messages = response.responseJSON.message;
    for(var i in messages) {
        if(messages[i].length > 1 ){
            for(var j in messages[i]){
                ul += "<li>" +j +": " + messages[i][j] + "</li>";
            }
        }else{
            ul += "<li>"+i +": " + messages[i] + "</li>";
        }
    }
    ul += "</ul>";
    return ul;
};

toastInfo = function (message){
    $.toast({
        heading: 'Error',
        text: message,
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
        text: message,
        position: 'top-right',
        loaderBg: '#ff6849',
        icon: 'warning',
        hideAfter: 6000,
        stack: 6
    });
};

toastError = function (message) { 
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
        heading: 'Success',
        text: message,
        position: 'top-right',
        loaderBg: '#ff6849',
        icon: 'success',
        hideAfter: 6000,
        stack: 6
    });
    
};

$(document).ready(function() {
    $('#birthday-icon, #birthday').MdPersianDateTimePicker({
        targetTextSelector: '#birthday',
        textFormat: 'yyyy-MM-dd',
        isGregorian: false,
        englishNumber: true,
        enableTimePicker: false,
    });
    $('#start_datetime-icon').MdPersianDateTimePicker({
        targetTextSelector: '#start_datetime',
        textFormat: 'yyyy-MM-dd HH:mm:ss',
        isGregorian: false,
        englishNumber: true,
        enableTimePicker: true,
        fromDate: true,
        groupId: 'leave_request_date',
    });
    $('#end_datetime-icon').MdPersianDateTimePicker({
        targetTextSelector: '#end_datetime',
        textFormat: 'yyyy-MM-dd HH:mm:ss',
        isGregorian: false,
        englishNumber: true,
        enableTimePicker: true,
        toDate: true,
        groupId: 'leave_request_date',
    });
});