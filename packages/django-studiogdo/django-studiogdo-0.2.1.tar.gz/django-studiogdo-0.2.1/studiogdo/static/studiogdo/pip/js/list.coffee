define ->

    class List

        fnSettings:
            "aaSorting": [ ]
            'aLengthMenu': [[25, 100, 500, -1], [25, 100, 500, 'Tous']]
            "bStateSave": true
            "bLengthChange" : true
            "iDisplayLength": 25
            "sDom": "Tlfrtip<'clear'>"
            "sPaginationType": "full_numbers"
            "oLanguage":
                "sLengthMenu": "Afficher _MENU_ lignes par page",
                "sZeroRecords": "Pas trouvé..",
                "sInfo": "Affichage de _START_ à _END_ sur _TOTAL_ lignes",
                "sInfoEmpty": "Affichage de 0 à 0 sur 0 lignes",
                "sInfoFiltered": "(filtrage sur _MAX_ lignes)",
                "sSearch" : "Rechercher"
                "oPaginate":
                    "sFirst" : "&nbsp;&nbsp;&nbsp;"
                    "sLast" : "&nbsp;&nbsp;&nbsp;"
                    "sNext" : "&nbsp;&nbsp;&nbsp;"
                    "sPrevious" : "&nbsp;&nbsp;&nbsp;"

        constructor: ->
            $(".list-details tr"). on "dblclick", (evt) =>
                row = $(evt.delegateTarget)
                details_path = row.data("apath")
                window.location.href = "/details/#{details_path}"

            $("table.datatable").dataTable(@fnSettings)
            @addDeleteButtons()

        addDeleteButtons: (msg="Voulez-vous réellement faire cette action?", where="tbody tr > td:last-child") =>
            ###
            Adds delete button on each line.
            Should be added after showListCallback
                showListCallback: (oSettings) =>
                super(oSettings)
                @addDeleteButtons()
            ###
            for td in $(".add-delete-bouton").find(where) when !($(td).hasClass("dataTables_empty") || $(td).hasClass("delete_button"))
                button = $('<span title="Détruire" class="glyphicon glyphicon-trash small"/>').appendTo(td)
                button.css('float', 'right')
                $(td).addClass("delete_button")
                button.on "click", (evt) =>
                    evt?.stopImmediatePropagation()
                    evt?.preventDefault()
                    if confirm "Confirmation : #{msg}"
                        tr = $(evt.delegateTarget).closest("tr")
                        path= tr.data("apath")
                        bocall = new BOCall
                        bocall.done = => window.location.reload()
                        bocall.applyCommand(path, "Unplug")
