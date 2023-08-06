(function(){
    var overcApplication = angular.module('overcApplication', ['ngResource', 'ui.router']);

    overcApplication.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider){
        //$urlRouterProvider.when('', '');
        $urlRouterProvider.otherwise('/overview'); // Redirect invalid URLs here

        $stateProvider.state('overview', {
            url: '/overview',
            templateUrl: 'page/overview.htm',
            abstract: true
        });

        $stateProvider.state('overview.all', {
            url: '',
            views: {
                overview: {
                    templateUrl: 'ctrl/overview.htm',
                    controller: 'servicesCtrl'
                }
            }
        });

        $stateProvider.state('detailed', {
            url: '/detailed',
            templateUrl: 'page/detailed.htm',
            abstract: true
        });

        $stateProvider.state('detailed.all', {
            url: '',
            views: {
                services: {
                    templateUrl: 'ctrl/services.htm',
                    controller: 'servicesCtrl'
                },
                alerts: {
                    templateUrl: 'ctrl/alerts.htm',
                    controller: 'alertsCtrl'
                }
            }
        });

        $stateProvider.state('service', {
            url: '/service/:service_id',
            templateUrl: 'page/service.htm',
            abstract: true
        });

        $stateProvider.state('service.view', {
            url: '',
            views: {
                service: {
                    templateUrl: 'ctrl/services.htm',
                    controller: 'servicesCtrl'
                },
                states: {
                    templateUrl: 'ctrl/states.htm',
                    controller: 'statesCtrl'
                },
                alerts: {
                    templateUrl: 'ctrl/alerts.htm',
                    controller: 'alertsCtrl'
                }
            }
        })
    }]);

    overcApplication.run(['$rootScope', '$state', '$stateParams', function($rootScope, $state, $stateParams){
        // Add these so they're accessible from any scope
        $rootScope.$state = $state;
        $rootScope.$stateParams = $stateParams;

        // Other global stuff
        $rootScope.state = {
            supervisor_lag: 0
        };
    }]);






    //region Services

    overcApplication.config(['$resourceProvider', function ($resourceProvider) {
        // Don't strip trailing slashes from calculated URLs
        //$resourceProvider.defaults.stripTrailingSlashes = false; // FIXME: Enable with AngularJS 1.3.0
    }]);


    /** API service
     */
    overcApplication.service('api', ['$resource', function($resource){
        /** Status API
         * @type {Object.<String, { get: Function }>}
         */
        this.status = {
            all: $resource('api/status/'),

            server: $resource('api/status/server/:server_id', {server_id: undefined}, {}),
            service: $resource('api/status/service/:service_id', {service_id: undefined}, {}),

            service_states: $resource('api/status/service/:service_id/states', {service_id: undefined}, {
                    get: { method: 'GET', params: { hours: 24, groups: undefined, expand: [] } }
                }),

            alerts: {
                all: $resource('api/status/alerts/', {}, {
                        get: { method: 'GET', params: { hours: 24 } }
                    }),
                server: $resource('api/status/alerts/server/:server_id', {server_id: undefined}, {
                        get: { method: 'GET', params: { hours: 24 } }
                    }),
                service: $resource('api/status/alerts/service/:service_id', {service_id: undefined}, {
                        get: { method: 'GET', params: { hours: 24 } }
                    })
            }
        };

        /** Items API
         * @type {Object.<String, { delete: Function }>}
         */
        this.items = {
            server: $resource('api/item/server/:server_id',
                {}, {}),
            service: $resource('api/item/service/:service_id',
                {}, {})
        };
    }]);

    /** Exchange service
     */
    overcApplication.service('X', ['$rootScope', function($rootScope){
        this.emit = $rootScope.$broadcast.bind($rootScope);
    }]);

    //endregion






    //region Controllers

    // TODO: push updates from the server (WOW!)

    /** Services controller
     *
     * State params:
     *      - server_id
     *      - service_id
     */
    overcApplication.controller('servicesCtrl', ['$rootScope', '$scope', '$state', '$interval', 'api', 'X', function($rootScope, $scope, $state, $interval, api, X){
        /** Known servers, services and their states
         * @type {Array}
         */
        $scope.servers = [];

        /** Statistics
         * @type {Object}
         */
        $scope.stats = {
            /** The number of alerts reported today
             */
            n_alerts: 0,
            /** Last known state
             */
            last_state_id: null
        };

        /** Action handlers
         */
        $scope.actions = {
            delete_server: function(server_id){
                api.items.server.delete({server_id: server_id}, function(res){
                    X.emit('update-services');
                });
            },
            delete_service: function(service_id){
                api.items.service.delete({service_id: service_id}, function(res){
                    X.emit('update-services');
                });
            }
        };

        // Auto-update servers
        var updateServers = function(){
            var callback = function(res){
                $scope.servers = res.servers;
                $scope.stats = res.stats;
                $rootScope.state.supervisor_lag = res.stats.supervisor_lag;

                // Set service state
                if ($state.params.service_id)
                    try { $state.title = $scope.servers[0].services[0].title; } catch(e){} // FIXME: this way of exporting the title is SHIT, but currently I have no better idea
            };

            if ($state.params.server_id)
                api.status.server.get({server_id: $state.params.server_id}, callback);
            else if ($state.params.service_id)
                api.status.service.get({service_id: $state.params.service_id}, callback);
            else
                api.status.all.get(callback);
        };
        var upd_int = setInterval(updateServers, 5000);
        $scope.$on('$destroy', function(){
            clearInterval(upd_int); // Need to clear the interval: otherwise, it will run even after the controller is dead
        });
        $scope.$on('update-services', updateServers);
        updateServers();

        // Auto-update alerts
        $scope.$watch('stats.n_alerts', function(val, oldVal){
            if (val != oldVal) {
                X.emit('update-alerts');
                X.emit('update-states');
            }
        });
        $scope.$watch('stats.last_state_id', function(val, oldVal){
            if (val != oldVal) {
                X.emit('update-states');
            }
        });
    }]);



    /** Service States controller
     */
    overcApplication.controller('statesCtrl', ['$scope', '$state', 'api', 'X', function($scope, $state, api, X){
        /** Settings
         * @type {Object}
         */
        $scope.sets = {
            /** States load period
             * @type {Number}
             */
            hours: 24,

            /** List of groups to expand
             * @type {Array.<Number>}
             */
            expand: []
        };

        /** Action handlers
         */
        $scope.actions = {
            /** Load more alerts
             */
            load_more_states: function(){
                $scope.sets.hours += 24;
            },
            /** Expand a group
             * @param {String} group
             */
            group_expand: function(group){
                $scope.sets.expand.push(group);
            }
        };

        /** States list
         * @type {Array}
         */
        $scope.states = [];

        var loadStates = function(){
            api.status.service_states.get({
                    service_id: $state.params.service_id,
                    hours: $scope.sets.hours,
                    groups: 'yes',
                    expand: $scope.sets.expand
            }, function(res){
                $scope.states = _.map(res.states, function(state){
                    // Assign CSS class property
                    _.each(state.alerts, function(alert){
                        alert.css_class = {
                            'OK': 'success', 'WARN': 'warning', 'FAIL': 'danger', 'UNK': 'default'
                        }[alert.severity];
                    });
                    return state;
                });
            });
        };

        $scope.$on('update-states', _.debounce(loadStates, 100));
        $scope.$watchCollection('sets.hours', function(val, oldVal){
            if (val != oldVal)
                loadStates();
        });
        $scope.$watchCollection('sets.expand', function(val, oldVal){
            if (val != oldVal)
                loadStates();
        });
    }]);



    /** Alerts controller
     */
    overcApplication.controller('alertsCtrl', ['$scope', '$state', 'api', 'X', function($scope, $state, api, X){
        /** Settings
         * @type {Object}
         */
        $scope.sets = {
            /** Alerts load period
             * @type {Number}
             */
            hours: 24
        };

        /** Action handlers
         */
        $scope.actions = {
            /** Load more alerts
             */
            load_more_alerts: function(){
                $scope.sets.hours += 24;
            }
        };

        /** Alerts list
         * @type {Array}
         */
        $scope.alerts = [];

        var loadAlerts = function(){
            var method = api.status.alerts.all,
                params = {
                    server_id: $state.params.server_id,
                    service_id: $state.params.service_id,
                    hours: $scope.sets.hours
                };
            if (params.server_id)
                method = api.status.alerts.server;
            if (params.service_id)
                method = api.status.alerts.service;

            method.get(params, function(res){
                $scope.alerts = res.alerts;
            });
        };

        $scope.$on('update-alerts', loadAlerts);
        $scope.$watch('sets.hours', function(val, oldVal){
            if (val != oldVal)
                loadAlerts();
        });
    }]);

    //endregion
})();
