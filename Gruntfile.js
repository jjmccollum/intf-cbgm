module.exports = function (grunt) {

    var py_files = ['**/*.py'];

    var afs =  grunt.option ('afs') || process.env.GRUNT_NTG_AFS || "/afs/rrz/vol/www/projekt/ntg";

    var localfs = grunt.option ('localfs') || process.env.GRUNT_NTG_LOCALFS ||
        "/var/www/ntg";

    var git_user = grunt.option ('gituser') || process.env.GRUNT_NTG_GITUSER;

    var browser = grunt.option ('browser') || process.env.GRUNT_BROWSER || "iceweasel";

    grunt.initConfig ({
        afs:            afs,
        localfs:        localfs,
        browser:        browser,
        rsync:          "rsync -rlptz --exclude='*~' --exclude='.*' --exclude='*.less' --exclude='node_modules'",
        wpcontent:      afs     + "/http/docs/wp-content",
        wpcontentlocal: localfs + "/wp-content",
        gituser:        git_user,
        pkg:            grunt.file.readJSON ('package.json'),

        less: {
            options: {
                banner: "/* Generated file. Do not edit. */\n",
                plugins: [
                    new (require ('less-plugin-autoprefix')) ({ browsers: ["last 2 versions"] })
                ]
            },
            production: {
                files: [
                    {
                        expand: true,
                        src: ['server/static/css/**/*.less'],
                        ext: '.css',
                        extDot: 'last'
                    }
                ]
            }
        },

        jshint: {
            options: {
                globals: {
                    jQuery: true
                }
            },
            files: ['Gruntfile.js', 'server/static/js/*.js']
        },

        pylint: {
            options: {
                force: true
            },
            server:  ['server/**/*.py'],
            scripts: ['scripts/cceh/**/*.py']
        },

        csslint: {
            options: {
                "adjoining-classes":      false,   // concerns IE6
                "box-sizing":             false,   // concerns IE6,7
                "ids":                    false,
                "overqualified-elements": false,
                "qualified-headings":     false,
            },
            src:  ['server/static/css/**/*.css']
        },

        pot: {
            options: {
                text_domain: "ntg",
                encoding: "utf-8",
                dest: 'languages/',
                keywords: ['__', '_e', '_n:1,2', '_x:1,2c'],
                msgmerge: true,
            },
            files: {
                src: py_files,
                expand: true,
            }
        },

        potomo: {
            themes: {
                options: {
                    poDel: false
                },
                files: [{
                    expand: true,
                    src: ['languages/*.po'],
                    dest: './',
                    ext: '.mo',
                    nonull: true,
                }]
            }
        },

        shell: {
            options: {
                cwd: ".",
                failOnError: false,
            },
            deploy: {
                command: '<%= rsync %> themes/ntg/* <%= wpcontent %>/themes/ntg/ ; <%= rsync %> plugins/cap-* <%= wpcontent %>/plugins/',
            },
            testdeploy: {
                command: '<%= rsync %> themes/ntg/* <%= wpcontentlocal %>/themes/ntg/ ; <%= rsync %> plugins/cap-* <%= wpcontentlocal %>/plugins/',
            },
        },

        watch: {
            files: ['<%= less.production.files %>'],
            tasks: ['less']
        }
    });

    grunt.loadNpmTasks ('grunt-contrib-csslint');
    grunt.loadNpmTasks ('grunt-contrib-jshint');
    grunt.loadNpmTasks ('grunt-contrib-less');
    grunt.loadNpmTasks ('grunt-contrib-watch');
    grunt.loadNpmTasks ('grunt-pot');
    grunt.loadNpmTasks ('grunt-potomo');
    grunt.loadNpmTasks ('grunt-pylint');
    grunt.loadNpmTasks ('grunt-shell');

    grunt.registerTask ('git',        ['shell:git-fetch-collation']);

    grunt.registerTask ('lint',       ['pylint', 'jshint']);
    grunt.registerTask ('mo',         ['pot', 'potomo']);
    grunt.registerTask ('testdeploy', ['lint', 'less', 'mo', 'shell:testdeploy']);
    grunt.registerTask ('deploy',     ['lint', 'less', 'mo', 'shell:deploy']);

    grunt.registerTask ('default',    ['jshint', 'less']);
};
