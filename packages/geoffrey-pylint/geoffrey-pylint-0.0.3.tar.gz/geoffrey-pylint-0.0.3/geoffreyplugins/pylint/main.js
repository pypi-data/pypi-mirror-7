$(function() {

  var PylintMessage = Backbone.Model.extend({

  });

  var PylintScore = Backbone.Model.extend({
    idAttribute: "filename"
  });

  var PylintMessages = Backbone.Collection.extend({
    model: PylintMessage,
    url: "/api/v1/states?" + $.param({
        project: project_id,
        plugin: "pylint",
        task: 'run_pylint',
        content_type: "data"
    }),
    initialize: function() {
      var this_ = this;

      this.listenTo(window.app, 'panel:enter:pylint', this.setUp);
      this.listenTo(window.app, 'panel:leave:pylint', this.tearDown);

    },
    setUp: function() {
      var this_ = this;
      window.app.subscribe(
          'pylint_messages',  // The name of this subscription.
          {  // The subscription criteria.
           'project': project_id,  // Global variable `project_id`
           'plugin': 'pylint',
           'content_type': 'data',
           'task': 'run_pylint'
          },
          function(data) {

            // Remove all messages of this key.
            toRemove = this_.filter(function(message){ 
              var key = message.get('filename');
              return key == data.key;
            });
            this_.remove(toRemove);

            // Parse & append new messages.
            var newMessages = this_.parseMessages(new Array(data));
            this_.add(newMessages);
          }
      );

    },
    tearDown: function() {
      window.app.unsubscribe('pylint_messages'); 
    },
    parse: function(response) {
      /* Unpack each message from each state */
      return this.parseMessages(response);
    },
    parseMessages: function(data) {
      var messages = new Array();
      for(var i=0; i<data.length; i++){
        var this_messages = data[i].value.messages;
        for(var m=0; m<this_messages.length; m++) {
            var current = {
              filename: data[i].key
            }
            _.extend(current, this_messages[m]);

            switch(current.C) {
              case "E":
              case "F":
                current.color = "danger"
                break;
              case "W":
              case "R":
                current.color = "warning"
                break;
              case "I":
              case "C":
                current.color = "info"
                break;
              default:
                current.color = "success"
                break;
            }

            messages.push(current);
        }
      }
      return messages;
    }
  });

  var PylintScores = Backbone.Collection.extend({
    model: PylintScore,
    url: "/api/v1/states?" + $.param({
        project: project_id,
        plugin: "pylint",
        task: "pylint_scores",
        content_type: "data"
    }),
    initialize: function() {

    this.listenTo(window.app, 'panel:enter:pylint', this.setUp);
    this.listenTo(window.app, 'panel:leave:pylint', this.tearDown);

    },
    setUp: function() {
      var this_ = this;

      window.app.subscribe(
          'pylint_scores',  // The name of this subscription.
          {  // The subscription criteria.
           'project': project_id,  // Global variable `project_id`
           'plugin': 'pylint',
           'content_type': 'data',
           'task': 'pylint_scores'
          },
          function(data) {
            this_.remove(this_.get(data.key));

            var newScore = this_.parseScores(new Array(data));
            this_.add(newScore);
          }
      );
    },
    tearDown: function() {
      window.app.unsubscribe('pylint_scores'); 
    },
    parse: function(response) {
      /* Unpack each message from each state */
      return this.parseScores(response);
    },
    parseScores: function(data) {
      var scores = new Array();
      for(var i=0; i<data.length; i++){
        var this_scores = data[i].value.scores;
        var last = _.last(this_scores);
        var current = {
          filename: data[i].key,
          scores: this_scores,
          last: last
        }

        switch(true) {
          case (last>=8):
            current.color = "success"
            break;
          case (last>=5 && last<8):
            current.color = "warning"
            break;
          case (last<5):
            current.color = "danger"
            break;
        }
        scores.push(current);
      }
      return scores;
    }
  });

  var PylintView = Backbone.View.extend({
    id: "pylint",
    initialize: function() {
      var this_ = this;

      this.messages = new PylintMessages();
      this.listenTo(this.messages, 'add', this.renderMessages);
      this.listenTo(this.messages, 'remove', this.renderMessages);
      this.listenTo(this.messages, 'reset', this.renderMessages);

      this.scores = new PylintScores();
      this.listenTo(this.scores, 'add', this.renderScores);
      this.listenTo(this.scores, 'remove', this.renderScores);
      this.listenTo(this.scores, 'reset', this.renderScores);

      this.listenTo(window.app, 'panel:enter:pylint', this.setUp);

      $.get("/plugins/pylint/panel.html", function(template){
        this_.template = _.template(template);
      }).done(function() { 
        this_.render();
      });
    },
    setUp: function() {
      this.messages.fetch({reset: true});
      this.scores.fetch({reset: true});
    },
    render: function() {
      this.$el.addClass("row");
      this.$el.html(this.template({
        messages: this.messages.toJSON(),
        scores: this.scores.toJSON()
      }));
      this.messagesTable = $('#pylint-messages').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false
      });
      this.scoresTable = $('#pylint-scores').dataTable({
        "bPaginate": true,
        "bLengthChange": false,
        "bFilter": true,
        "bSort": true,
        "bInfo": true,
        "bAutoWidth": false,
        "fnDrawCallback": this.drawGraphs
      });

      this.renderMessages();
      this.renderScores();
    },
    renderMessages: function() {
      this.messagesTable.fnClearTable();
      if(this.messages.models){
        var oSettings = this.messagesTable.fnSettings();
        for(var i=0; i<this.messages.models.length; i++){
          var row = this.messages.models[i];
          var a = this.messagesTable.fnAddData([
            row.get("msg_id"),
            row.get("module"),
            row.get("line"),
            row.get("column"),
            row.get("msg"),
            row.get("filename")], false);
          var nTr = oSettings.aoData[ a[0] ].nTr;
          $(nTr).addClass(row.get("color"));
        }
      }

      this.messagesTable.fnDraw();

    },
    renderScores: function() {
      this.scoresTable.fnClearTable();
      if(this.scores.models){
        var oSettings = this.scoresTable.fnSettings();
        for(var i=0; i<this.scores.models.length; i++){
          var row = this.scores.models[i];
          var scores = row.get("scores");
          var evolution = "<span class='pylintscorehistory' values='" + scores.join() + "'></span>";
          var a = this.scoresTable.fnAddData([evolution, _.last(scores), row.get("filename")], false);
          var nTr = oSettings.aoData[ a[0] ].anCells[1];
          $(nTr).addClass(row.get("color"));
        }
      }

      this.scoresTable.fnDraw();

    },
    drawGraphs: function() {
      $(".pylintscorehistory").sparkline("html", {
          type: "bar",
          chartRangeMax: 10,
          chartRangeMin: 0,
          zeroAxis: false,
          colorMap: $.range_map({
            ':5': '#f56954',
            '5:8': '#f39c12',
            '8:': '#00a65a'})
          }
      );
    }
  });
   
  var entry = new window.MenuEntry({
     title: "PyLint",
     subtitle: "Python code static checker",
     route: "pylint",
     icon: "fa-check-square-o",
     content: new PylintView(),
  });

  window.app.registerMenu(entry);

});
