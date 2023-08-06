var STATIC_ROOT = '{{static_root}}';

module.exports = function(grunt) {
    
    // Configure plugins.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
       
        sass: {
          dev: {
            files: [{
                expand: true,
                cwd: STATIC_ROOT+'/scss',
                src: ['{,*/}*.{scss,sass}'],
                dest: STATIC_ROOT+'/css',
                ext: '.css'
                }]
          },
        },
        watch: {
            options: {livereload: true},
            sass: {
                files: STATIC_ROOT+'/scss/{,*/}*.{scss,sass}',
                tasks: ['sass:dev']
            }
        }
    });
    
    // Load plugins here.
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');

    // Register tasks here.
    grunt.registerTask('default', ["watch"]);
};