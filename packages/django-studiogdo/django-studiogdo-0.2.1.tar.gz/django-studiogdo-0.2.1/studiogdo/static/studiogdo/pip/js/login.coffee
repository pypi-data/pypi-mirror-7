define ->

    class Login

        constructor: ->
            $("#password").on "keypress", @passwdKeyPress

        passwdKeyPress: (evt) =>
            which = evt.which
            shift_status = evt.shiftKey
            maj = ((which >= 65 && which <= 90) && !shift_status) || ((which >= 97 && which <= 122) && shift_status)
            if maj
                $("#alertMaj").show()
            else
                $("#alertMaj").hide()

    new Login