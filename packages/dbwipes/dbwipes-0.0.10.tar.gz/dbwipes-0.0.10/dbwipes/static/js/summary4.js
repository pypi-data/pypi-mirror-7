requirejs.config({
  //By default load any module IDs from js/lib
  baseUrl: '/static/js/lib',

  //except, if the module ID starts with "app",
  //load it from the js/app directory. paths
  //config is relative to the baseUrl, and
  //never includes a ".js" extension since
  //the paths config could be for a directory.
  paths: {
    summary: '../summary'
  },

  shim: {
    'backbone': {
      //These script dependencies should be loaded before loading
      //backbone.js
      deps: ['underscore', 'jquery'],
      //Once loaded, use the global 'Backbone' as the
      //module value.
      exports: 'Backbone'
    },
    'underscore': {
      exports: '_'
    },
    'jquery': {
      exports: '$'
    },
    'handlebars': {
      exports: 'Handlebars'
    },
    'bootstrap': {
      deps: ['jquery'],
      exports: '$'
    },
    'bootstrap-slider': {
      deps: ['bootstrap'],
      exports: '$'
    },
    'tether': {
      exports: 'Tether'
    },
    'shepherd': {
      deps: ['jquery', 'tether', 'backbone'],
      exports: 'Shepherd'
    }
  }
});

// Start the main app logic.
requirejs(['jquery', 
           'd3',
           'summary/util',
           'summary/setup',
           'summary/task',
           'underscore',
           'shepherd',
           'handlebars',
           'bootstrap',
           'bootstrap-slider'
  ], function ($, d3, util, setup, TaskView, _, Shepherd, Handlebars) {

  $ = require('bootstrap-slider');

  setup.setupBasic();
  setup.setupButtons(window.q, window.qv);
  setup.setupScorpion(window.enableScorpion, window.q, window.qv, window.where);
  setup.setupTuples(window.q, window.srv, window.where);




  var testq1 = {
    x: 'day',
    ys: [{col: 'amt', expr: 'sum(amt)'}],
    schema: {
      x: 'num',
      amt: 'num'
    },
    table: 'test',
    db: 'test'
  };
  var testq2 = _.extend(_.clone(testq1), {
    ys: [{col: 'amt', expr: 'avg(amt)'}]
  })

  q.set(testq1);

  var checkAnswer = function(answer, task) {
    if (answer == null || answer == '' || answer.length == 0) {
      return "Please enter an answer";
    }
    return true;
  };
  var wheretemplate = Handlebars.compile($("#where-ans-template").html());

  var tasks = [
    new TaskView({
      question: "<p> What subset of the data is most responsible for the increase in sales?</p>",
      text: $("#q1-template").html(),
      textbox: false,
      attachTo: '#tasks',
      truth: function(answer, task) {
        if (answer == null || answer == '' || answer.length == 0) {
          return "Please select a filter";
        }
        return true;
      },
      on: {
        'show': function(task) {
          function onChange() {
            var models = _.compact(window.where.map(function(model) {
              var sel = model.get('selection'),
                  vals = _.keys(sel);
              if (vals.length) return model;
            }));
            $("#q1-answer").empty();
            var clauses = _.map(models, function(model, idx) { 
              var sql = util.negateClause(model.toSQLWhere());
              var json = { idx: idx, sql: sql};
              $("#q1-answer").append($(wheretemplate(json)));
              return sql;
            });
            //$("#q1-answer").html(clauses.join('<br/>')).show();
            task.model.set('answer', models);
          }
          window.where.on('change:selection', onChange);
          task.on('submit', function() {
            window.where.off('change:selection', onChange);
          });
        }
      }
    }),
    new TaskView({
      question: $("#q2-template").html(),
      textbox: true,
      truth: checkAnswer,
      attachTo: '#tasks',
    }),
    new TaskView({
      question: $("#q3-template").html(),
      textbox: true,
      truth: checkAnswer,
      attachTo: '#tasks',
    }),
    new TaskView({
      question: $("#q4-template").html(),
      options: [ 
        'not confident', 
        'somwhat confident',
        'very confident',
        'without a doubt'
      ],
      textbox: true,
      truth: checkAnswer,
      attachTo: '#tasks',
      on: {
        'submit': function() {
          q.set(testq2);
        }
      }
    }),
    new TaskView({
      question: $("#q5-question").html(),
      text: $("#q5-text").html(),
      textbox: false,
      truth: function(answer) {
        return false;
      },
      attachTo: '#tasks',
      truth: function(answer, task) {
        if (answer == null || answer == '' || answer.length == 0) {
          return "Please select a filter";
        }
        return true;
      },
      on: {
        'show': function(task) {
          qv.state.yscales.domain([75, 100]);
          qv.yzoom.y(qv.state.yscales);
          qv.yzoom.event(qv.c);
          qv.c.select('.yaxis').call(qv.state.yaxis);

          function onChange() {
            var models = _.compact(window.where.map(function(model) {
              var sel = model.get('selection'),
                  vals = _.keys(sel);
              if (vals.length) return model;
            }));
            $("#q5-answer").empty();
            var clauses = _.map(models, function(model, idx) { 
              var sql = util.negateClause(model.toSQLWhere());
              var json = { idx: idx, sql: sql};
              $("#q5-answer").append($(wheretemplate(json)));
              return sql;
            });
            //$("#q5-answer").html(clauses.join('<br/>')).show();
            task.model.set('answer', models);
          }
          window.where.on('change:selection', onChange);
          task.on('submit', function() {
            window.where.off('change:selection', onChange);
          });
        }
      }
    }),
    new TaskView({
      question: $("#q2-template").html(),
      textbox: true,
      truth: checkAnswer,
      attachTo: '#tasks',
    }),
    new TaskView({
      question: $("#q3-template").html(),
      textbox: true,
      truth: checkAnswer,
      attachTo: '#tasks',
    }),
    new TaskView({
      question: $("#q4-template").html(),
      options: [ 
        'not confident', 
        'somwhat confident',
        'very confident',
        'without a doubt'
      ],
      textbox: true,
      truth: checkAnswer,
      attachTo: '#tasks',
      on: {
        'submit': function() {
          q.set(testq2);
        }
      }
    })
  ];
  _.each(tasks, function(task, idx) {
    var prefix = "Q" + (idx+1) + " of " + tasks.length;
    var title = task.model.get('title') || "";
    task.model.set('title', prefix + " " + title);
    task.on('submit', function() {
      _.delay(function() {
        task.hide();
        if (tasks[idx+1]) {
          tasks[idx+1].show();
        } else {
          tour.show('end');
        }
      }, 1500);
    });
  })


  var tour = new Shepherd.Tour({
    defaults: { classes: "shepherd-element shepherd-open shepherd-theme-arrows"}
  });

  var btns = [{
      text: 'Back',
      action: tour.back
    },{
      text: 'Next',
      action: tour.next
    }];
  var backbtn = [{
    text: 'Back',
    action: tour.back
  }];
  var step;


  step = tour.addStep('start', {
    title: "Validation",
    text: $("#start-template").html(),
    classes: "shepherd shepherd-open shepherd-theme-arrows shepherd-transparent-text",
    style: { width: 600 },
    buttons: [{
      text: "Next",
      action: function() {
        $("div.row").css("opacity", 1); 
        tasks[0].show();
        tour.cancel();
      }
    }]
  });
  step.on("show", function() { $("div.row").css("opacity", 0.6); });
  step.on("hide", function() { $("div.row").css("opacity", 1); });


  step = tour.addStep('end', {
    title: "Done!",
    text: "<p>Thank You!</p>"+
          "<p>Please press Exit to go back to the main directory when you are ready.</p>",
    classes: "shepherd shepherd-open shepherd-theme-arrows shepherd-transparent-text",
    showCancelLink: true,
    buttons: [{
      text: 'Exit',
      action: function () {
        window.location = '/dir/';
      }
    }],
    style: { width: 500 }
  });
  step.on("show", function() { $("div.row").css("opacity", 0.6); });
  step.on("hide", function() { $("div.row").css("opacity", 1); });



  tour.start();
  window.tour = tour;

});
