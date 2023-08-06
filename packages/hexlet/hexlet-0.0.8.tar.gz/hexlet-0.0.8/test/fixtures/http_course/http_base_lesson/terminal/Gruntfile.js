module.exports = function(grunt) {
  grunt.loadNpmTasks('grunt-karma');
  grunt.loadNpmTasks('grunt-contrib-requirejs');

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    requirejs: {
      compile: {
        options: {
          optimize: "none",
          baseUrl: "./",

          appDir: "js",
          dir: 'dist',
          modules: [{
            name: 'http10'
          }, {
            name: 'http11'
          }, {
            name: 'postRequest'
          }]
        }
      }
    },

    karma: {
      unit: {
          configFile: 'karma.conf.js',
          autoWatch: true
        }
    }
  });
};
