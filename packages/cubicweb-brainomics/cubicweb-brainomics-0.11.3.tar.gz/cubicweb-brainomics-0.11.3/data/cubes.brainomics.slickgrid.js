Slick.Formatters['HTML'] = function HTMLFormatter(row, cell, value, columnDef, dataContext) {
    return value;
};

function cwSlickGrid(divid, data, columns, options){
    $.each(columns, function(index, value) {
        if(typeof value.formatter != "undefined") {
            value.formatter = Slick.Formatters[value.formatter];
        }
    });
    var dataView = new Slick.Data.DataView();
    // set data
    dataView.setItems(data);
    // render the grid
    var grid = new Slick.Grid(divid, dataView, columns, options);

    // wire up model events to drive the grid
    dataView.onRowCountChanged.subscribe(function (e, args) {
        grid.updateRowCount();
        grid.render();
        });

    dataView.onRowsChanged.subscribe(function (e, args) {
        grid.invalidateRows(args.rows);
        grid.render();
    });

    grid.onSort.subscribe(function(e, args) {
        // a simple comparer function here.
        // if args.multiColumnSort : args.sortCols will have an array of
        // {sortCol:..., sortAsc:...}
        var comparer = function(a, b) {
        return (a[args.sortCol.field] > b[args.sortCol.field]) ? 1 : -1;
        };
        dataView.sort(comparer, args.sortAsc);
    });

};
