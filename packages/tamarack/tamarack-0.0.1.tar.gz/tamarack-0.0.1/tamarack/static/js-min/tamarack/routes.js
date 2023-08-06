// Compiled by ClojureScript 0.0-2234
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
secretary.core.set_config_BANG_(cljs.core.constant$keyword$101,"#");
tamarack.routes.merge_query_params = (function merge_query_params(query_params,state){if(cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2(cljs.core.constant$keyword$96.cljs$core$IFn$_invoke$arity$1(query_params),"false"))
{var from = (new Date(cljs.core.constant$keyword$109.cljs$core$IFn$_invoke$arity$1(query_params)));var to = (new Date(cljs.core.constant$keyword$110.cljs$core$IFn$_invoke$arity$1(query_params)));var timeslice = new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$23,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [from,to], null),cljs.core.constant$keyword$96,false], null);return cljs.core.merge.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$100,timeslice], null),state], 0));
} else
{if(cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2(cljs.core.constant$keyword$96.cljs$core$IFn$_invoke$arity$1(query_params),"true"))
{var window_size = parseInt(cljs.core.constant$keyword$111.cljs$core$IFn$_invoke$arity$1(query_params),10);var window = tamarack.state.timeslice_ending_now(window_size);var timeslice = new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$23,window,cljs.core.constant$keyword$97,window_size,cljs.core.constant$keyword$96,true], null);return cljs.core.merge.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$100,timeslice], null),state], 0));
} else
{if(cljs.core.constant$keyword$6)
{return state;
} else
{return null;
}
}
}
});
var action__6934__auto___7253 = (function (params__6935__auto__){if(cljs.core.map_QMARK_(params__6935__auto__))
{var map__7251 = params__6935__auto__;var map__7251__$1 = ((cljs.core.seq_QMARK_(map__7251))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__7251):map__7251);var query_params = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7251__$1,cljs.core.constant$keyword$108);return tamarack.routes.merge_query_params(query_params,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$112,cljs.core.constant$keyword$113,cljs.core.constant$keyword$98,null], null));
} else
{if(cljs.core.vector_QMARK_(params__6935__auto__))
{var vec__7252 = params__6935__auto__;var query_params = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7252,0,null);return tamarack.routes.merge_query_params(query_params,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$112,cljs.core.constant$keyword$113,cljs.core.constant$keyword$98,null], null));
} else
{return null;
}
}
});secretary.core.add_route_BANG_("/",action__6934__auto___7253);
/**
* @param {...*} var_args
*/
tamarack.routes.all_apps = ((function (action__6934__auto___7253){
return (function() { 
var all_apps__delegate = function (args__6933__auto__){return cljs.core.apply.cljs$core$IFn$_invoke$arity$3(secretary.core.render_route_STAR_,"/",args__6933__auto__);
};
var all_apps = function (var_args){
var args__6933__auto__ = null;if (arguments.length > 0) {
  args__6933__auto__ = cljs.core.array_seq(Array.prototype.slice.call(arguments, 0),0);} 
return all_apps__delegate.call(this,args__6933__auto__);};
all_apps.cljs$lang$maxFixedArity = 0;
all_apps.cljs$lang$applyTo = (function (arglist__7254){
var args__6933__auto__ = cljs.core.seq(arglist__7254);
return all_apps__delegate(args__6933__auto__);
});
all_apps.cljs$core$IFn$_invoke$arity$variadic = all_apps__delegate;
return all_apps;
})()
;})(action__6934__auto___7253))
;
var action__6934__auto___7257 = (function (params__6935__auto__){if(cljs.core.map_QMARK_(params__6935__auto__))
{var map__7255 = params__6935__auto__;var map__7255__$1 = ((cljs.core.seq_QMARK_(map__7255))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__7255):map__7255);var query_params = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7255__$1,cljs.core.constant$keyword$108);var id = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7255__$1,cljs.core.constant$keyword$34);return tamarack.routes.merge_query_params(query_params,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$112,cljs.core.constant$keyword$114,cljs.core.constant$keyword$98,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$99,id], null)], null));
} else
{if(cljs.core.vector_QMARK_(params__6935__auto__))
{var vec__7256 = params__6935__auto__;var id = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7256,0,null);var query_params = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7256,1,null);return tamarack.routes.merge_query_params(query_params,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$112,cljs.core.constant$keyword$114,cljs.core.constant$keyword$98,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$99,id], null)], null));
} else
{return null;
}
}
});secretary.core.add_route_BANG_("/applications/:id",action__6934__auto___7257);
/**
* @param {...*} var_args
*/
tamarack.routes.app_dashboard = ((function (action__6934__auto___7257){
return (function() { 
var app_dashboard__delegate = function (args__6933__auto__){return cljs.core.apply.cljs$core$IFn$_invoke$arity$3(secretary.core.render_route_STAR_,"/applications/:id",args__6933__auto__);
};
var app_dashboard = function (var_args){
var args__6933__auto__ = null;if (arguments.length > 0) {
  args__6933__auto__ = cljs.core.array_seq(Array.prototype.slice.call(arguments, 0),0);} 
return app_dashboard__delegate.call(this,args__6933__auto__);};
app_dashboard.cljs$lang$maxFixedArity = 0;
app_dashboard.cljs$lang$applyTo = (function (arglist__7258){
var args__6933__auto__ = cljs.core.seq(arglist__7258);
return app_dashboard__delegate(args__6933__auto__);
});
app_dashboard.cljs$core$IFn$_invoke$arity$variadic = app_dashboard__delegate;
return app_dashboard;
})()
;})(action__6934__auto___7257))
;
var action__6934__auto___7261 = (function (params__6935__auto__){if(cljs.core.map_QMARK_(params__6935__auto__))
{var map__7259 = params__6935__auto__;var map__7259__$1 = ((cljs.core.seq_QMARK_(map__7259))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__7259):map__7259);var query_params = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7259__$1,cljs.core.constant$keyword$108);var endpoint = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7259__$1,cljs.core.constant$keyword$115);var id = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7259__$1,cljs.core.constant$keyword$34);return tamarack.routes.merge_query_params(query_params,new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$112,cljs.core.constant$keyword$117,cljs.core.constant$keyword$98,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$99,id], null),cljs.core.constant$keyword$116,endpoint], null));
} else
{if(cljs.core.vector_QMARK_(params__6935__auto__))
{var vec__7260 = params__6935__auto__;var id = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7260,0,null);var endpoint = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7260,1,null);var query_params = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7260,2,null);return tamarack.routes.merge_query_params(query_params,new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$112,cljs.core.constant$keyword$117,cljs.core.constant$keyword$98,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$99,id], null),cljs.core.constant$keyword$116,endpoint], null));
} else
{return null;
}
}
});secretary.core.add_route_BANG_("/applications/:id/:endpoint",action__6934__auto___7261);
/**
* @param {...*} var_args
*/
tamarack.routes.app_endpoint_overview = ((function (action__6934__auto___7261){
return (function() { 
var app_endpoint_overview__delegate = function (args__6933__auto__){return cljs.core.apply.cljs$core$IFn$_invoke$arity$3(secretary.core.render_route_STAR_,"/applications/:id/:endpoint",args__6933__auto__);
};
var app_endpoint_overview = function (var_args){
var args__6933__auto__ = null;if (arguments.length > 0) {
  args__6933__auto__ = cljs.core.array_seq(Array.prototype.slice.call(arguments, 0),0);} 
return app_endpoint_overview__delegate.call(this,args__6933__auto__);};
app_endpoint_overview.cljs$lang$maxFixedArity = 0;
app_endpoint_overview.cljs$lang$applyTo = (function (arglist__7262){
var args__6933__auto__ = cljs.core.seq(arglist__7262);
return app_endpoint_overview__delegate(args__6933__auto__);
});
app_endpoint_overview.cljs$core$IFn$_invoke$arity$variadic = app_endpoint_overview__delegate;
return app_endpoint_overview;
})()
;})(action__6934__auto___7261))
;
tamarack.routes.timeslice_query_params = (function timeslice_query_params(){var timeslice = cljs.core.constant$keyword$100.cljs$core$IFn$_invoke$arity$1(cljs.core.deref(tamarack.state.app_state));var vec__7264 = cljs.core.constant$keyword$23.cljs$core$IFn$_invoke$arity$1(timeslice);var from = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7264,0,null);var to = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7264,1,null);if(cljs.core.truth_(cljs.core.constant$keyword$96.cljs$core$IFn$_invoke$arity$1(timeslice)))
{return new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$111,cljs.core.constant$keyword$97.cljs$core$IFn$_invoke$arity$1(timeslice),cljs.core.constant$keyword$96,true], null);
} else
{return new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$109,from.toISOString(),cljs.core.constant$keyword$110,to.toISOString(),cljs.core.constant$keyword$96,false], null);
}
});
tamarack.routes.remove_default_query_params = (function remove_default_query_params(params){var remove_tracking_now = (function remove_tracking_now(params__$1){if(cljs.core.truth_(cljs.core.constant$keyword$96.cljs$core$IFn$_invoke$arity$1(params__$1)))
{return cljs.core.dissoc.cljs$core$IFn$_invoke$arity$2(params__$1,cljs.core.constant$keyword$96);
} else
{return params__$1;
}
});
var remove_window_size = (function remove_window_size(params__$1){if(cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2(tamarack.state.default_tracking_now_window_size,cljs.core.constant$keyword$111.cljs$core$IFn$_invoke$arity$1(params__$1)))
{return cljs.core.dissoc.cljs$core$IFn$_invoke$arity$2(params__$1,cljs.core.constant$keyword$111);
} else
{return params__$1;
}
});
var remove_conflicting = (function remove_conflicting(params__$1){if((cljs.core.constant$keyword$96.cljs$core$IFn$_invoke$arity$1(params__$1) == null))
{return cljs.core.dissoc.cljs$core$IFn$_invoke$arity$variadic(params__$1,cljs.core.constant$keyword$109,cljs.core.array_seq([cljs.core.constant$keyword$110], 0));
} else
{return cljs.core.dissoc.cljs$core$IFn$_invoke$arity$2(params__$1,cljs.core.constant$keyword$111);
}
});
return cljs.core.comp.cljs$core$IFn$_invoke$arity$3(remove_conflicting,remove_tracking_now,remove_window_size).call(null,params);
});
tamarack.routes.remove_route_defaults = (function remove_route_defaults(route){return cljs.core.update_in.cljs$core$IFn$_invoke$arity$3(route,new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$108], null),tamarack.routes.remove_default_query_params);
});
tamarack.routes.cleanup_query_params = (function cleanup_query_params(route){if(cljs.core.empty_QMARK_(cljs.core.constant$keyword$108.cljs$core$IFn$_invoke$arity$1(route)))
{return cljs.core.dissoc.cljs$core$IFn$_invoke$arity$2(route,cljs.core.constant$keyword$108);
} else
{return route;
}
});
tamarack.routes.url_of = (function() {
var url_of = null;
var url_of__1 = (function (route){return url_of.cljs$core$IFn$_invoke$arity$2(route,cljs.core.PersistentArrayMap.EMPTY);
});
var url_of__2 = (function (route,arg){return (route.cljs$core$IFn$_invoke$arity$1 ? route.cljs$core$IFn$_invoke$arity$1(tamarack.routes.cleanup_query_params(tamarack.routes.remove_route_defaults(cljs.core.merge.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$108,tamarack.routes.timeslice_query_params()], null),arg], 0))))) : route.call(null,tamarack.routes.cleanup_query_params(tamarack.routes.remove_route_defaults(cljs.core.merge.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$108,tamarack.routes.timeslice_query_params()], null),arg], 0))))));
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
var navigate_to__1 = (function (route){return navigate_to.cljs$core$IFn$_invoke$arity$2(route,cljs.core.PersistentArrayMap.EMPTY);
});
var navigate_to__2 = (function (route,arg){var url = tamarack.routes.url_of.cljs$core$IFn$_invoke$arity$2(route,arg);return tamarack.history.history.setToken(cljs.core.subs.cljs$core$IFn$_invoke$arity$2(url,1));
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
tamarack.routes.refresh_timeslice = (function refresh_timeslice(){var token = tamarack.history.history.getToken();var qpos = token.indexOf("?");var vec__7266 = ((cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2(qpos,-1))?new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [token,""], null):new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.subs.cljs$core$IFn$_invoke$arity$3(token,0,qpos),cljs.core.subs.cljs$core$IFn$_invoke$arity$2(token,(qpos + 1))], null));var path = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7266,0,null);var query_string = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7266,1,null);var query_params = secretary.core.decode_query_params(query_string);var new_query_params = tamarack.routes.remove_default_query_params(cljs.core.merge.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([query_params,tamarack.routes.timeslice_query_params()], 0)));var new_query_string = secretary.core.encode_query_params(new_query_params);var token__$1 = ((cljs.core.empty_QMARK_(new_query_string))?path:clojure.string.join.cljs$core$IFn$_invoke$arity$2("?",new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [path,new_query_string], null)));return tamarack.history.history.setToken(token__$1);
});
