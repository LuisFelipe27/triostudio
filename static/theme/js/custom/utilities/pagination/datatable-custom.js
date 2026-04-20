"use strict";

// Class definition
var KTDatatableCustom = function () {
    // Shared variables
    var table;
    var datatable;

    // Private functions
    var initDatatable = function (url, columns, columnsDefs, orderColumns) {

        datatable = $(table).DataTable({
            "info": false,
            "language": {
              "zeroRecords": "No hay registros para mostrar",
              "processing": "Cargando..."
            },
            order: orderColumns,
            processing: true,
            serverSide: true,
            ajax: {
                url: url,
                dataSrc: "data",
            },
            columns: columns,
            columnDefs: columnsDefs
        });

        datatable.on('draw', function () {
            KTMenu.createInstances();
        });
    }

    // Filter Datatable
    var handleFilterDatatable = (filters) => {
        filters.forEach(filter => {
            let filterSelector = document.querySelector(filter.selector);
            $(filterSelector).on('change', e => {
                let value = e.target.value;
                if (value === 'all') {
                    value = '';
                }
                datatable.column(filter.column).search(value).draw();
            });
        });
    }

    // Init daterangepicker
    var initDaterangepicker = (selector) => {
        var start = moment().subtract(29, "days");
        var end = moment();
        var input = $(selector);

        function cb(start, end) {
            input.html(start.format("MMMM D, YYYY") + " - " + end.format("MMMM D, YYYY"));
        }

        input.daterangepicker({
            language: 'es',
            locale: {
                format: "DD/MM/YYYY",
                customRangeLabel: 'Rango',
                cancelLabel: 'Cancelar',
                applyLabel: 'Aplicar',
            },
            startDate: start,
            endDate: end,
            ranges: {
                "Hoy": [moment(), moment()],
                "Ayer": [moment().subtract(1, "days"), moment().subtract(1, "days")],
                "Últimos 7 dias": [moment().subtract(6, "days"), moment()],
                "Últimos 30 dias": [moment().subtract(29, "days"), moment()],
                "Este Mes": [moment().startOf("month"), moment().endOf("month")],
                "Mes Pasado": [moment().subtract(1, "month").startOf("month"), moment().subtract(1, "month").endOf("month")]
            }
        }, cb);

        cb(start, end);
    }

    // Hook export buttons
    var exportButtons = (export_input, export_menu, export_title, export_options) => {
        const documentTitle = export_title;
        var buttons = new $.fn.dataTable.Buttons(table, {
            buttons: [
                {
                    extend: 'copyHtml5',
                    title: documentTitle
                },
                {
                    extend: 'excelHtml5',
                    title: documentTitle,
                    exportOptions: export_options
                },
                {
                    extend: 'csvHtml5',
                    title: documentTitle
                },
                {
                    extend: 'pdfHtml5',
                    title: documentTitle,
                    orientation: 'landscape',
                    pageSize: 'LEGAL',
                    exportOptions: export_options
                }
            ]
        }).container().appendTo(export_input);

        // Hook dropdown menu click event to datatable export buttons
        const exportButtons = document.querySelectorAll(export_menu + ' [data-kt-export]');
        exportButtons.forEach(exportButton => {
            exportButton.addEventListener('click', e => {
                e.preventDefault();

                // Get clicked export value
                const exportValue = e.target.getAttribute('data-kt-export');
                const target = document.querySelector('.dt-buttons .buttons-' + exportValue);

                // Trigger click event on hidden datatable export buttons
                target.click();
            });
        });
    }


    // Search Datatable --- official docs reference: https://datatables.net/reference/api/search()
    var handleSearchDatatable = (selector) => {
        const filterSearch = document.querySelector(selector);
        filterSearch.addEventListener('keyup', function (e) {
            datatable.search(e.target.value).draw();
        });
    }

    // Public methods
    return {
        init: function (selectors, url, columns, filters, columnsDefs, orderColumns) {
            if('table' in selectors && selectors.table){
                table = document.querySelector(selectors.table);

                if (!table) {
                    return;
                }
                if(!orderColumns){
                    orderColumns = [];
                }
                if(url && columns && columnsDefs){
                    initDatatable(url, columns, columnsDefs, orderColumns);
                }
            }

            if('daterangepicker' in selectors && selectors.daterangepicker){
                initDaterangepicker(selectors.daterangepicker);
            }

            if('export' in selectors && 'export_menu' in selectors && 'export_title' in selectors && 'export_options' in selectors){
                if(selectors.export && selectors.export_menu && selectors.export_title && selectors.export_options){
                    exportButtons(selectors.export, selectors.export_menu, selectors.export_title, selectors.export_options);
                }
            }

            if('search' in selectors && selectors.search){
               handleSearchDatatable(selectors.search);
            }
            if(filters){
              handleFilterDatatable(filters);
            }

        }
    };
}();