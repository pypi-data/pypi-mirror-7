// Compiled by ClojureScript 0.0-2268
goog.provide('tamarack.routes');
goog.require('cljs.core');
goog.require('goog.History');
goog.require('tamarack.state');
goog.require('tamarack.state');
goog.require('tamarack.history');
goog.require('tamarack.history');
goog.require('secretary.core');
goog.require('secretary.core');
goog.require('clojure.string');
goog.require('clojure.string');
secretary.core.set_config_BANG_.call(null,new cljs.core.Keyword(null,"prefix","prefix",-265908465),"#");
tamarack.routes.merge_query_params = (function merge_query_params(query_params,state){if(cljs.core._EQ_.call(null,new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757).cljs$core$IFn$_invoke$arity$1(query_params),"false"))
{var from = (new Date(new cljs.core.Keyword(null,"from","from",1815293044).cljs$core$IFn$_invoke$arity$1(query_params)));var to = (new Date(new cljs.core.Keyword(null,"to","to",192099007).cljs$core$IFn$_invoke$arity$1(query_params)));var timeslice = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"window","window",724519534),new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [from,to], null),new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757),false], null);return cljs.core.merge.call(null,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"timeslice","timeslice",446627929),timeslice], null),state);
} else
{if(cljs.core._EQ_.call(null,new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757).cljs$core$IFn$_invoke$arity$1(query_params),"true"))
{var window_size = parseInt(new cljs.core.Keyword(null,"last","last",1105735132).cljs$core$IFn$_invoke$arity$1(query_params),(10));var window = tamarack.state.timeslice_ending_now.call(null,window_size);var timeslice = new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"window","window",724519534),window,new cljs.core.Keyword(null,"window-size","window-size",923834855),window_size,new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757),true], null);return cljs.core.merge.call(null,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"timeslice","timeslice",446627929),timeslice], null),state);
} else
{if(new cljs.core.Keyword(null,"else","else",-1508377146))
{return state;
} else
{return null;
}
}
}
});
var action__6983__auto___7286 = (function (params__6984__auto__){if(cljs.core.map_QMARK_.call(null,params__6984__auto__))
{var map__7284 = params__6984__auto__;var map__7284__$1 = ((cljs.core.seq_QMARK_.call(null,map__7284))?cljs.core.apply.call(null,cljs.core.hash_map,map__7284):map__7284);var query_params = cljs.core.get.call(null,map__7284__$1,new cljs.core.Keyword(null,"query-params","query-params",900640534));return tamarack.routes.merge_query_params.call(null,query_params,new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"view","view",1247994814),new cljs.core.Keyword(null,"all-apps","all-apps",1203012863),new cljs.core.Keyword(null,"current-app","current-app",1533042174),null], null));
} else
{if(cljs.core.vector_QMARK_.call(null,params__6984__auto__))
{var vec__7285 = params__6984__auto__;var query_params = cljs.core.nth.call(null,vec__7285,(0),null);return tamarack.routes.merge_query_params.call(null,query_params,new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"view","view",1247994814),new cljs.core.Keyword(null,"all-apps","all-apps",1203012863),new cljs.core.Keyword(null,"current-app","current-app",1533042174),null], null));
} else
{return null;
}
}
});secretary.core.add_route_BANG_.call(null,"/",action__6983__auto___7286);
/**
* @param {...*} var_args
*/
tamarack.routes.all_apps = ((function (action__6983__auto___7286){
return (function() { 
var all_apps__delegate = function (args__6982__auto__){return cljs.core.apply.call(null,secretary.core.render_route_STAR_,"/",args__6982__auto__);
};
var all_apps = function (var_args){
var args__6982__auto__ = null;if (arguments.length > 0) {
  args__6982__auto__ = cljs.core.array_seq(Array.prototype.slice.call(arguments, 0),0);} 
return all_apps__delegate.call(this,args__6982__auto__);};
all_apps.cljs$lang$maxFixedArity = 0;
all_apps.cljs$lang$applyTo = (function (arglist__7287){
var args__6982__auto__ = cljs.core.seq(arglist__7287);
return all_apps__delegate(args__6982__auto__);
});
all_apps.cljs$core$IFn$_invoke$arity$variadic = all_apps__delegate;
return all_apps;
})()
;})(action__6983__auto___7286))
;
var action__6983__auto___7290 = (function (params__6984__auto__){if(cljs.core.map_QMARK_.call(null,params__6984__auto__))
{var map__7288 = params__6984__auto__;var map__7288__$1 = ((cljs.core.seq_QMARK_.call(null,map__7288))?cljs.core.apply.call(null,cljs.core.hash_map,map__7288):map__7288);var query_params = cljs.core.get.call(null,map__7288__$1,new cljs.core.Keyword(null,"query-params","query-params",900640534));var id = cljs.core.get.call(null,map__7288__$1,new cljs.core.Keyword(null,"id","id",-1388402092));return tamarack.routes.merge_query_params.call(null,query_params,new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"view","view",1247994814),new cljs.core.Keyword(null,"app-dashboard","app-dashboard",-106677937),new cljs.core.Keyword(null,"current-app","current-app",1533042174),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"name","name",1843675177),id], null)], null));
} else
{if(cljs.core.vector_QMARK_.call(null,params__6984__auto__))
{var vec__7289 = params__6984__auto__;var id = cljs.core.nth.call(null,vec__7289,(0),null);var query_params = cljs.core.nth.call(null,vec__7289,(1),null);return tamarack.routes.merge_query_params.call(null,query_params,new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"view","view",1247994814),new cljs.core.Keyword(null,"app-dashboard","app-dashboard",-106677937),new cljs.core.Keyword(null,"current-app","current-app",1533042174),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"name","name",1843675177),id], null)], null));
} else
{return null;
}
}
});secretary.core.add_route_BANG_.call(null,"/applications/:id",action__6983__auto___7290);
/**
* @param {...*} var_args
*/
tamarack.routes.app_dashboard = ((function (action__6983__auto___7290){
return (function() { 
var app_dashboard__delegate = function (args__6982__auto__){return cljs.core.apply.call(null,secretary.core.render_route_STAR_,"/applications/:id",args__6982__auto__);
};
var app_dashboard = function (var_args){
var args__6982__auto__ = null;if (arguments.length > 0) {
  args__6982__auto__ = cljs.core.array_seq(Array.prototype.slice.call(arguments, 0),0);} 
return app_dashboard__delegate.call(this,args__6982__auto__);};
app_dashboard.cljs$lang$maxFixedArity = 0;
app_dashboard.cljs$lang$applyTo = (function (arglist__7291){
var args__6982__auto__ = cljs.core.seq(arglist__7291);
return app_dashboard__delegate(args__6982__auto__);
});
app_dashboard.cljs$core$IFn$_invoke$arity$variadic = app_dashboard__delegate;
return app_dashboard;
})()
;})(action__6983__auto___7290))
;
var action__6983__auto___7294 = (function (params__6984__auto__){if(cljs.core.map_QMARK_.call(null,params__6984__auto__))
{var map__7292 = params__6984__auto__;var map__7292__$1 = ((cljs.core.seq_QMARK_.call(null,map__7292))?cljs.core.apply.call(null,cljs.core.hash_map,map__7292):map__7292);var query_params = cljs.core.get.call(null,map__7292__$1,new cljs.core.Keyword(null,"query-params","query-params",900640534));var endpoint = cljs.core.get.call(null,map__7292__$1,new cljs.core.Keyword(null,"endpoint","endpoint",447890044));var id = cljs.core.get.call(null,map__7292__$1,new cljs.core.Keyword(null,"id","id",-1388402092));return tamarack.routes.merge_query_params.call(null,query_params,new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"view","view",1247994814),new cljs.core.Keyword(null,"app-endpoint-overview","app-endpoint-overview",486981663),new cljs.core.Keyword(null,"current-app","current-app",1533042174),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"name","name",1843675177),id], null),new cljs.core.Keyword(null,"current-endpoint","current-endpoint",-28327621),endpoint], null));
} else
{if(cljs.core.vector_QMARK_.call(null,params__6984__auto__))
{var vec__7293 = params__6984__auto__;var id = cljs.core.nth.call(null,vec__7293,(0),null);var endpoint = cljs.core.nth.call(null,vec__7293,(1),null);var query_params = cljs.core.nth.call(null,vec__7293,(2),null);return tamarack.routes.merge_query_params.call(null,query_params,new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"view","view",1247994814),new cljs.core.Keyword(null,"app-endpoint-overview","app-endpoint-overview",486981663),new cljs.core.Keyword(null,"current-app","current-app",1533042174),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"name","name",1843675177),id], null),new cljs.core.Keyword(null,"current-endpoint","current-endpoint",-28327621),endpoint], null));
} else
{return null;
}
}
});secretary.core.add_route_BANG_.call(null,"/applications/:id/:endpoint",action__6983__auto___7294);
/**
* @param {...*} var_args
*/
tamarack.routes.app_endpoint_overview = ((function (action__6983__auto___7294){
return (function() { 
var app_endpoint_overview__delegate = function (args__6982__auto__){return cljs.core.apply.call(null,secretary.core.render_route_STAR_,"/applications/:id/:endpoint",args__6982__auto__);
};
var app_endpoint_overview = function (var_args){
var args__6982__auto__ = null;if (arguments.length > 0) {
  args__6982__auto__ = cljs.core.array_seq(Array.prototype.slice.call(arguments, 0),0);} 
return app_endpoint_overview__delegate.call(this,args__6982__auto__);};
app_endpoint_overview.cljs$lang$maxFixedArity = 0;
app_endpoint_overview.cljs$lang$applyTo = (function (arglist__7295){
var args__6982__auto__ = cljs.core.seq(arglist__7295);
return app_endpoint_overview__delegate(args__6982__auto__);
});
app_endpoint_overview.cljs$core$IFn$_invoke$arity$variadic = app_endpoint_overview__delegate;
return app_endpoint_overview;
})()
;})(action__6983__auto___7294))
;
tamarack.routes.timeslice_query_params = (function timeslice_query_params(){var timeslice = new cljs.core.Keyword(null,"timeslice","timeslice",446627929).cljs$core$IFn$_invoke$arity$1(cljs.core.deref.call(null,tamarack.state.app_state));var vec__7297 = new cljs.core.Keyword(null,"window","window",724519534).cljs$core$IFn$_invoke$arity$1(timeslice);var from = cljs.core.nth.call(null,vec__7297,(0),null);var to = cljs.core.nth.call(null,vec__7297,(1),null);if(cljs.core.truth_(new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757).cljs$core$IFn$_invoke$arity$1(timeslice)))
{return new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"last","last",1105735132),new cljs.core.Keyword(null,"window-size","window-size",923834855).cljs$core$IFn$_invoke$arity$1(timeslice),new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757),true], null);
} else
{return new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"from","from",1815293044),from.toISOString(),new cljs.core.Keyword(null,"to","to",192099007),to.toISOString(),new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757),false], null);
}
});
tamarack.routes.remove_default_query_params = (function remove_default_query_params(params){var remove_tracking_now = (function remove_tracking_now(params__$1){if(cljs.core.truth_(new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757).cljs$core$IFn$_invoke$arity$1(params__$1)))
{return cljs.core.dissoc.call(null,params__$1,new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757));
} else
{return params__$1;
}
});
var remove_window_size = (function remove_window_size(params__$1){if(cljs.core._EQ_.call(null,tamarack.state.default_tracking_now_window_size,new cljs.core.Keyword(null,"last","last",1105735132).cljs$core$IFn$_invoke$arity$1(params__$1)))
{return cljs.core.dissoc.call(null,params__$1,new cljs.core.Keyword(null,"last","last",1105735132));
} else
{return params__$1;
}
});
var remove_conflicting = (function remove_conflicting(params__$1){if((new cljs.core.Keyword(null,"tracking-now","tracking-now",-2134671757).cljs$core$IFn$_invoke$arity$1(params__$1) == null))
{return cljs.core.dissoc.call(null,params__$1,new cljs.core.Keyword(null,"from","from",1815293044),new cljs.core.Keyword(null,"to","to",192099007));
} else
{return cljs.core.dissoc.call(null,params__$1,new cljs.core.Keyword(null,"last","last",1105735132));
}
});
return cljs.core.comp.call(null,remove_conflicting,remove_tracking_now,remove_window_size).call(null,params);
});
tamarack.routes.remove_route_defaults = (function remove_route_defaults(route){return cljs.core.update_in.call(null,route,new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"query-params","query-params",900640534)], null),tamarack.routes.remove_default_query_params);
});
tamarack.routes.cleanup_query_params = (function cleanup_query_params(route){if(cljs.core.empty_QMARK_.call(null,new cljs.core.Keyword(null,"query-params","query-params",900640534).cljs$core$IFn$_invoke$arity$1(route)))
{return cljs.core.dissoc.call(null,route,new cljs.core.Keyword(null,"query-params","query-params",900640534));
} else
{return route;
}
});
tamarack.routes.url_of = (function() {
var url_of = null;
var url_of__1 = (function (route){return url_of.call(null,route,cljs.core.PersistentArrayMap.EMPTY);
});
var url_of__2 = (function (route,arg){return route.call(null,tamarack.routes.cleanup_query_params.call(null,tamarack.routes.remove_route_defaults.call(null,cljs.core.merge.call(null,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"query-params","query-params",900640534),tamarack.routes.timeslice_query_params.call(null)], null),arg))));
});
url_of = function(route,arg){
switch(arguments.length){
case 1:
return url_of__1.call(this,route);
case 2:
return url_of__2.call(this,route,arg);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
url_of.cljs$core$IFn$_invoke$arity$1 = url_of__1;
url_of.cljs$core$IFn$_invoke$arity$2 = url_of__2;
return url_of;
})()
;
tamarack.routes.navigate_to = (function() {
var navigate_to = null;
var navigate_to__1 = (function (route){return navigate_to.call(null,route,cljs.core.PersistentArrayMap.EMPTY);
});
var navigate_to__2 = (function (route,arg){var url = tamarack.routes.url_of.call(null,route,arg);return tamarack.history.history.setToken(cljs.core.subs.call(null,url,(1)));
});
navigate_to = function(route,arg){
switch(arguments.length){
case 1:
return navigate_to__1.call(this,route);
case 2:
return navigate_to__2.call(this,route,arg);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
navigate_to.cljs$core$IFn$_invoke$arity$1 = navigate_to__1;
navigate_to.cljs$core$IFn$_invoke$arity$2 = navigate_to__2;
return navigate_to;
})()
;
tamarack.routes.refresh_timeslice = (function refresh_timeslice(){var token = tamarack.history.history.getToken();var qpos = token.indexOf("?");var vec__7299 = ((cljs.core._EQ_.call(null,qpos,(-1)))?new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [token,""], null):new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.subs.call(null,token,(0),qpos),cljs.core.subs.call(null,token,(qpos + (1)))], null));var path = cljs.core.nth.call(null,vec__7299,(0),null);var query_string = cljs.core.nth.call(null,vec__7299,(1),null);var query_params = secretary.core.decode_query_params.call(null,query_string);var new_query_params = tamarack.routes.remove_default_query_params.call(null,cljs.core.merge.call(null,query_params,tamarack.routes.timeslice_query_params.call(null)));var new_query_string = secretary.core.encode_query_params.call(null,new_query_params);var token__$1 = ((cljs.core.empty_QMARK_.call(null,new_query_string))?path:clojure.string.join.call(null,"?",new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [path,new_query_string], null)));return tamarack.history.history.setToken(token__$1);
});

//# sourceMappingURL=routes.js.map