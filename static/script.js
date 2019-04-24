

let $messages = $('#messages')

$messages.on('click', ".like", async function(e) {
    e.preventDefault()
    let messageId = $(e.target).attr('id')
    let res = await $.post({
        url: `/messages/${messageId}/add`
    })

})