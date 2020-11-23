get_min_temp = async () => {
    result = await fetch("/min_temp")
    result = await result.json()
    result = result['min_temp']
    return result
}


refresh_min_temp = async () => {
    temp = await get_min_temp()
    temp = String(temp)
    $("#min-temp").attr("placeholder", `Current: ${temp}`)
    $("#min-temp").val("")
}


var notifier_status = async () => {
    result = await fetch("/mail?action=status")
    result = await result.json()
    result = result['enabled']
    if (result == '0') {
        return false
    } else if (result == '1') {
        return true
    }
}

var start_notifier = async () => {
    await fetch("/mail?action=start")
}


var stop_notifier = async () => {
    await fetch("/mail?action=stop")
}


set_min_temp = async (temp) => {
    await fetch("/set_min_temp?temp=" + temp)
}

remove_recipient = async (recipient) => {
    console.log(`removing ${recipient}`)
    result = await fetch("/recipients?action=remove&recipient=" + recipient)
}

get_recipients = async () => {
    result = await fetch("/recipients?action=get_recipients")
    console.log(result)
    result = await result.json()
    
    return result['recipients']
}


add_recipient = async (recipient) => {
    result = await fetch("/recipients?action=add&recipient=" + recipient)
}

refresh_recipients = async() => {
    var recipients = await get_recipients()
    
    var ul = $(".ul-recipients")
    ul.empty()
    recipients.forEach(element => {
        if (element != "") {
            ul.append(`
            <li class="li-recipient">
                <div class="recipient-box">
                    <span class="recipient-name">${element}</span>
                    <button class="remove-recipient-btn" value="${element}">remove</button>
                </div>
            </li>`
            )
        }    
    });
    
}


$(".btn-test-mail").click(function() {
    fetch("/send_test_mail")
})



load_items = async () => {
    await refresh_min_temp()
    await refresh_recipients()

    $(document).on('click', '.remove-recipient-btn', async function(event) {

        console.log("remove recipient ")
        var mail = event.currentTarget.value
        await remove_recipient(mail)
        refresh_recipients();
        
    });

    // $(".remove-recipient-btn").on("click", async function(event) {
        
    // })

    $(".add-recipient-btn").click(async () => {
        var recipient = await $(".input-recipient").val()
        await add_recipient(recipient)
        $(".input-recipient").val("")
        await refresh_recipients()    
       
    });

    $("#change-min-temp-btn").click(async () => {
        var new_temp = $("#min-temp").val()
        await set_min_temp(new_temp)
        await refresh_min_temp()
    });


    first_time = true
    $("#input-on-off").change(async function() {
        // if (first_time) {
        //     status = await notifier_status()
            
        // }
        if (!first_time) {
            console.log("changed")
            checked = $(this).prop('checked')
            if (checked) {
                start_notifier()
            } else {
                stop_notifier()
            }
        }  
        first_time = false
    });

    if (await notifier_status()) {
        $("#input-on-off").bootstrapToggle('on')
    } else {
        $("#input-on-off").bootstrapToggle('off')
    }
    

}

load_items()