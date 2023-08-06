$(function() {

  var RadonCCMetric = Backbone.Model.extend({
  });

  var RadonMIMetric = Backbone.Model.extend({
    idAttribute: "filename"

  });

  var RadonMIMetrics = Backbone.Collection.extend({
    model: RadonMIMetric,
    url: "/api/v1/states?" + $.param({
        project: project_id,
        plugin: "radon",
        task: "mi_histogram",
        content_type: "data"
    }),
    initialize: function() {
      var this_ = this;

      this.listenTo(window.app, 'panel:enter:radon', this.setUp);
      this.listenTo(window.app, 'panel:leave:radon', this.tearDown);

    },
    setUp: function () {
      var this_ = this;
      window.app.subscribe(
          'radon_mi',  // The name of this subscription.
          {  // The subscription criteria.
           'project': project_id,  // Global variable `project_id`
           'plugin': 'radon',
           'task': 'mi_histogram',
           'content_type': 'data'
          },
          function(data) {
            this_.remove(this_.get(data.key));

            var newMetric = this_.parseMetrics([data]);
            this_.add(newMetric);
          }
      );
    },
    tearDown: function () {
      window.app.unsubscribe('radon_mi'); 
    },
    parse: function (response) {
      return this.parseMetrics(response);
    },
    parseMetrics: function (data) {
      var metrics = []; 
      for(var i=0; i<data.length; i++) {
          var current = data[i];
          var last_rank = _.last(current.value.ranks);

          var current_mi = {
            filename: current.key,
            scores: current.value.scores,
            ranks: current.value.ranks,
            last_score: _.last(current.value.scores),
            last_rank: last_rank,
          };
          switch(last_rank) {
            case "A":
              current_mi.color = "success";
              break;
            case "B":
              current_mi.color = "warning";
              break;
            case "C":
              current_mi.color = "danger";
              break;
            default:
              current_mi.color = "info"
              break;
          }
          metrics.push(current_mi);
      }
      return metrics;
    }
  });

  var RadonCCMetrics = Backbone.Collection.extend({
    model: RadonCCMetric,
    url: "/api/v1/states?" + $.param({
        project: project_id,
        plugin: "radon",
        task: "cc_histogram",
        content_type: "data"
    }),
    initialize: function() {
      var this_ = this;

      this.listenTo(window.app, 'panel:enter:radon', this.setUp);
      this.listenTo(window.app, 'panel:leave:radon', this.tearDown);

    },
    setUp: function() {
      var this_ = this;
      window.app.subscribe(
          'radon_cc',  // The name of this subscription.
          {  // The subscription criteria.
           'project': project_id,  // Global variable `project_id`
           'plugin': 'radon',
           'task': 'cc_histogram',
           'content_type': 'data'
          },
          function(data) {
            this_.remove(this_.where({'filename': data.key}));

            var newMetric = this_.parseMetrics([data]);
            this_.add(newMetric);
          }
      );
    },
    tearDown: function() {
      window.app.unsubscribe('radon_cc'); 
    },
    parse: function(response) {
      return this.parseMetrics(response);
    },
    parseMetrics: function(data) {
      var metrics = [];
      for(var i=0; i<data.length; i++) {
          var current = data[i].value.data;
          for(var s=0; s<current.length; s++) {
              var symbol = current[s];

              var last_rank = _.last(symbol.ranks);
    
              var current_cc = {
                id: data[i].key + ':' + symbol.fqn,
                filename: data[i].key,
                object: symbol.fqn,
                ranks: symbol.ranks,
                complexities: symbol.complexities,
                last_rank: last_rank,
                last_complexity: _.last(symbol.complexities),
              };
    
              switch(last_rank) {
                case "A":
                  current_cc.color = "success";
                  break;
                case "B":
                  current_cc.color = "warning";
                  break;
                default:
                  current_cc.color = "danger";
                  break;
              }
              metrics.push(current_cc);
          }
      }
      return metrics;
    }
  });

  var RadonView = Backbone.View.extend({
    id: "radon",
    initialize: function() {
      var this_ = this;
      this.cc = new RadonCCMetrics();
      this.listenTo(this.cc, 'add', this.renderCC);
      this.listenTo(this.cc, 'remove', this.renderCC);
      this.listenTo(this.cc, 'reset', this.renderCC);

      this.mi = new RadonMIMetrics();
      this.listenTo(this.mi, 'add', this.renderMI);
      this.listenTo(this.mi, 'remove', this.renderMI);
      this.listenTo(this.mi, 'reset', this.renderMI);

      this.listenTo(window.app, 'panel:enter:radon', this.setUp);

      $.get("/plugins/radon/panel.html", function(template){
        this_.template = _.template(template);
      }).done(function() { 
        this_.render();
      });

    },
    setUp: function() {
      this.cc.fetch({reset: true});
      this.mi.fetch({reset: true});
    },
    render: function() {
      this.$el.addClass("row");
      this.$el.html(this.template({ }));
      this.MITable = $('#radon-mi').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        "fnDrawCallback": this.drawMIGraphs
      });
      this.CCTable = $('#radon-cc').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        "fnDrawCallback": this.drawCCGraphs
      });
    },
    renderMI: function() {
      this.MITable.fnClearTable();
      if(this.mi.models){
        var oSettings = this.MITable.fnSettings();
        for(var i=0; i<this.mi.models.length; i++){
          var row = this.mi.models[i];

          var scores = row.get("scores");
          var ranks = row.get("ranks");

          var evolution = "<span class='radonmihistory' scores='" + scores.join() + "' ranks='" + ranks.join() + "'></span>";
          var a = this.MITable.fnAddData([
            evolution,
            row.get("last_rank"),
            row.get("last_score"),
            row.get("filename")], false);
          var nTr = oSettings.aoData[ a[0] ].anCells[1];
          $(nTr).addClass(row.get("color"));
        }
      }
      this.MITable.fnDraw();
    },
    renderCC: function() {
      this.CCTable.fnClearTable();
      if(this.cc.models){
        var oSettings = this.CCTable.fnSettings();
        for(var i=0; i<this.cc.models.length; i++){
          var row = this.cc.models[i];

          var ranks = row.get("ranks");
          var complexities = row.get("complexities");

          var evolution = "<span class='radoncchistory' ranks='" + ranks.join() + "' complexities='" + complexities.join() + "'></span>";
          var a = this.CCTable.fnAddData([
            evolution,
            row.get("last_rank"),
            row.get("last_complexity"),
            row.get("filename"),
            row.get("object"),
            ], false);
          var nTr = oSettings.aoData[ a[0] ].anCells[1];
          $(nTr).addClass(row.get("color"));
        }
      }
      this.CCTable.fnDraw();
    },
    drawMIGraphs: function() {
      $(".radonmihistory").sparkline("html", {
          type: "bar",
          chartRangeMax: 10,
          chartRangeMin: 0,
          zeroAxis: false,
          composite: false,
          tagValuesAttribute: "scores",
          colorMap: $.range_map({
            ':9': '#f56954',
            '9:19': '#f39c12',
            '19:': '#00a65a'})
          }
      );
    },
    drawCCGraphs: function() {
      $(".radoncchistory").sparkline("html", {
          type: "bar",
          chartRangeMax: 10,
          chartRangeMin: 0,
          zeroAxis: false,
          composite: false,
          tagValuesAttribute: "complexities",
          colorMap: $.range_map({
            '10:': '#f56954',
            '6:10': '#f39c12',
            ':5': '#00a65a'})
          }
      );
    },
  });

  var entry = new window.MenuEntry({
     title: "Radon",
     subtitle: "Code Metrics in Python",
     route: "radon",
     icon: "fa-check-square-o",
     content: new RadonView(),
  });

  window.app.registerMenu(entry);
});
