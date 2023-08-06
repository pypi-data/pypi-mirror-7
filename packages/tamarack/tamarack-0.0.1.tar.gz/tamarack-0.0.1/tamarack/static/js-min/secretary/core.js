// Compiled by ClojureScript 0.0-2234
goog.provide('secretary.core');
goog.require('cljs.core');
goog.require('clojure.walk');
goog.require('clojure.walk');
goog.require('clojure.string');
goog.require('clojure.string');
secretary.core.IRouteMatches = (function (){var obj8852 = {};return obj8852;
})();
secretary.core.route_matches = (function route_matches(this$,route){if((function (){var and__3561__auto__ = this$;if(and__3561__auto__)
{return this$.secretary$core$IRouteMatches$route_matches$arity$2;
} else
{return and__3561__auto__;
}
})())
{return this$.secretary$core$IRouteMatches$route_matches$arity$2(this$,route);
} else
{var x__4200__auto__ = (((this$ == null))?null:this$);return (function (){var or__3573__auto__ = (secretary.core.route_matches[goog.typeOf(x__4200__auto__)]);if(or__3573__auto__)
{return or__3573__auto__;
} else
{var or__3573__auto____$1 = (secretary.core.route_matches["_"]);if(or__3573__auto____$1)
{return or__3573__auto____$1;
} else
{throw cljs.core.missing_protocol("IRouteMatches.route-matches",this$);
}
}
})().call(null,this$,route);
}
});
secretary.core.IRouteValue = (function (){var obj8854 = {};return obj8854;
})();
secretary.core.route_value = (function route_value(this$){if((function (){var and__3561__auto__ = this$;if(and__3561__auto__)
{return this$.secretary$core$IRouteValue$route_value$arity$1;
} else
{return and__3561__auto__;
}
})())
{return this$.secretary$core$IRouteValue$route_value$arity$1(this$);
} else
{var x__4200__auto__ = (((this$ == null))?null:this$);return (function (){var or__3573__auto__ = (secretary.core.route_value[goog.typeOf(x__4200__auto__)]);if(or__3573__auto__)
{return or__3573__auto__;
} else
{var or__3573__auto____$1 = (secretary.core.route_value["_"]);if(or__3573__auto____$1)
{return or__3573__auto____$1;
} else
{throw cljs.core.missing_protocol("IRouteValue.route-value",this$);
}
}
})().call(null,this$);
}
});
secretary.core.IRenderRoute = (function (){var obj8856 = {};return obj8856;
})();
secretary.core.render_route = (function() {
var render_route = null;
var render_route__1 = (function (this$){if((function (){var and__3561__auto__ = this$;if(and__3561__auto__)
{return this$.secretary$core$IRenderRoute$render_route$arity$1;
} else
{return and__3561__auto__;
}
})())
{return this$.secretary$core$IRenderRoute$render_route$arity$1(this$);
} else
{var x__4200__auto__ = (((this$ == null))?null:this$);return (function (){var or__3573__auto__ = (secretary.core.render_route[goog.typeOf(x__4200__auto__)]);if(or__3573__auto__)
{return or__3573__auto__;
} else
{var or__3573__auto____$1 = (secretary.core.render_route["_"]);if(or__3573__auto____$1)
{return or__3573__auto____$1;
} else
{throw cljs.core.missing_protocol("IRenderRoute.render-route",this$);
}
}
})().call(null,this$);
}
});
var render_route__2 = (function (this$,params){if((function (){var and__3561__auto__ = this$;if(and__3561__auto__)
{return this$.secretary$core$IRenderRoute$render_route$arity$2;
} else
{return and__3561__auto__;
}
})())
{return this$.secretary$core$IRenderRoute$render_route$arity$2(this$,params);
} else
{var x__4200__auto__ = (((this$ == null))?null:this$);return (function (){var or__3573__auto__ = (secretary.core.render_route[goog.typeOf(x__4200__auto__)]);if(or__3573__auto__)
{return or__3573__auto__;
} else
{var or__3573__auto____$1 = (secretary.core.render_route["_"]);if(or__3573__auto____$1)
{return or__3573__auto____$1;
} else
{throw cljs.core.missing_protocol("IRenderRoute.render-route",this$);
}
}
})().call(null,this$,params);
}
});
render_route = function(this$,params){
switch(arguments.length){
case 1:
return render_route__1.call(this,this$);
case 2:
return render_route__2.call(this,this$,params);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
render_route.cljs$core$IFn$_invoke$arity$1 = render_route__1;
render_route.cljs$core$IFn$_invoke$arity$2 = render_route__2;
return render_route;
})()
;
secretary.core._STAR_config_STAR_ = cljs.core.atom.cljs$core$IFn$_invoke$arity$1(new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$101,""], null));
/**
* Gets a value for *config* at path.
*/
secretary.core.get_config = (function get_config(path){var path__$1 = ((cljs.core.sequential_QMARK_(path))?path:new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [path], null));return cljs.core.get_in.cljs$core$IFn$_invoke$arity$2(cljs.core.deref(secretary.core._STAR_config_STAR_),path__$1);
});
/**
* Associates a value val for *config* at path.
*/
secretary.core.set_config_BANG_ = (function set_config_BANG_(path,val){var path__$1 = ((cljs.core.sequential_QMARK_(path))?path:new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [path], null));return cljs.core.swap_BANG_.cljs$core$IFn$_invoke$arity$4(secretary.core._STAR_config_STAR_,cljs.core.assoc_in,path__$1,val);
});
secretary.core.encode = encodeURIComponent;
/**
* Given a key and a value return and encoded key-value pair.
*/
secretary.core.encode_pair = (function (){var method_table__4439__auto__ = cljs.core.atom.cljs$core$IFn$_invoke$arity$1(cljs.core.PersistentArrayMap.EMPTY);var prefer_table__4440__auto__ = cljs.core.atom.cljs$core$IFn$_invoke$arity$1(cljs.core.PersistentArrayMap.EMPTY);var method_cache__4441__auto__ = cljs.core.atom.cljs$core$IFn$_invoke$arity$1(cljs.core.PersistentArrayMap.EMPTY);var cached_hierarchy__4442__auto__ = cljs.core.atom.cljs$core$IFn$_invoke$arity$1(cljs.core.PersistentArrayMap.EMPTY);var hierarchy__4443__auto__ = cljs.core.get.cljs$core$IFn$_invoke$arity$3(cljs.core.PersistentArrayMap.EMPTY,cljs.core.constant$keyword$102,cljs.core.get_global_hierarchy());return (new cljs.core.MultiFn("encode-pair",((function (method_table__4439__auto__,prefer_table__4440__auto__,method_cache__4441__auto__,cached_hierarchy__4442__auto__,hierarchy__4443__auto__){
return (function (p__8857){var vec__8858 = p__8857;var k = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8858,0,null);var v = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8858,1,null);if((cljs.core.sequential_QMARK_(v)) || (cljs.core.set_QMARK_(v)))
{return cljs.core.constant$keyword$103;
} else
{if((function (){var or__3573__auto__ = cljs.core.map_QMARK_(v);if(or__3573__auto__)
{return or__3573__auto__;
} else
{var G__8860 = v;if(G__8860)
{var bit__4223__auto__ = (G__8860.cljs$lang$protocol_mask$partition0$ & 67108864);if((bit__4223__auto__) || (G__8860.cljs$core$IRecord$))
{return true;
} else
{if((!G__8860.cljs$lang$protocol_mask$partition0$))
{return cljs.core.native_satisfies_QMARK_(cljs.core.IRecord,G__8860);
} else
{return false;
}
}
} else
{return cljs.core.native_satisfies_QMARK_(cljs.core.IRecord,G__8860);
}
}
})())
{return cljs.core.constant$keyword$104;
} else
{return null;
}
}
});})(method_table__4439__auto__,prefer_table__4440__auto__,method_cache__4441__auto__,cached_hierarchy__4442__auto__,hierarchy__4443__auto__))
,cljs.core.constant$keyword$7,hierarchy__4443__auto__,method_table__4439__auto__,prefer_table__4440__auto__,method_cache__4441__auto__,cached_hierarchy__4442__auto__));
})();
secretary.core.key_index = (function() {
var key_index = null;
var key_index__1 = (function (k){return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(cljs.core.name(k))+"[]");
});
var key_index__2 = (function (k,index){return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(cljs.core.name(k))+"["+cljs.core.str.cljs$core$IFn$_invoke$arity$1(index)+"]");
});
key_index = function(k,index){
switch(arguments.length){
case 1:
return key_index__1.call(this,k);
case 2:
return key_index__2.call(this,k,index);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
key_index.cljs$core$IFn$_invoke$arity$1 = key_index__1;
key_index.cljs$core$IFn$_invoke$arity$2 = key_index__2;
return key_index;
})()
;
secretary.core.encode_pair.cljs$core$IMultiFn$_add_method$arity$3(null,cljs.core.constant$keyword$103,(function (p__8861){var vec__8862 = p__8861;var k = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8862,0,null);var v = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8862,1,null);var encoded = cljs.core.map_indexed(((function (vec__8862,k,v){
return (function (i,x){var pair = ((cljs.core.coll_QMARK_(x))?new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [secretary.core.key_index.cljs$core$IFn$_invoke$arity$2(k,i),x], null):new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [secretary.core.key_index.cljs$core$IFn$_invoke$arity$1(k),x], null));return (secretary.core.encode_pair.cljs$core$IFn$_invoke$arity$1 ? secretary.core.encode_pair.cljs$core$IFn$_invoke$arity$1(pair) : secretary.core.encode_pair.call(null,pair));
});})(vec__8862,k,v))
,v);return clojure.string.join.cljs$core$IFn$_invoke$arity$2("&",encoded);
}));
secretary.core.encode_pair.cljs$core$IMultiFn$_add_method$arity$3(null,cljs.core.constant$keyword$104,(function (p__8863){var vec__8864 = p__8863;var k = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8864,0,null);var v = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8864,1,null);var encoded = cljs.core.map.cljs$core$IFn$_invoke$arity$2(((function (vec__8864,k,v){
return (function (p__8865){var vec__8866 = p__8865;var ik = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8866,0,null);var iv = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8866,1,null);return (secretary.core.encode_pair.cljs$core$IFn$_invoke$arity$1 ? secretary.core.encode_pair.cljs$core$IFn$_invoke$arity$1(new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [secretary.core.key_index.cljs$core$IFn$_invoke$arity$2(k,cljs.core.name(ik)),iv], null)) : secretary.core.encode_pair.call(null,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [secretary.core.key_index.cljs$core$IFn$_invoke$arity$2(k,cljs.core.name(ik)),iv], null)));
});})(vec__8864,k,v))
,v);return clojure.string.join.cljs$core$IFn$_invoke$arity$2("&",encoded);
}));
secretary.core.encode_pair.cljs$core$IMultiFn$_add_method$arity$3(null,cljs.core.constant$keyword$7,(function (p__8867){var vec__8868 = p__8867;var k = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8868,0,null);var v = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8868,1,null);return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(cljs.core.name(k))+"="+cljs.core.str.cljs$core$IFn$_invoke$arity$1((secretary.core.encode.cljs$core$IFn$_invoke$arity$1 ? secretary.core.encode.cljs$core$IFn$_invoke$arity$1((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(v))) : secretary.core.encode.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(v))))));
}));
/**
* Convert a map of query parameters into url encoded string.
*/
secretary.core.encode_query_params = (function encode_query_params(query_params){return clojure.string.join.cljs$core$IFn$_invoke$arity$2("&",cljs.core.map.cljs$core$IFn$_invoke$arity$2(secretary.core.encode_pair,query_params));
});
/**
* Like js/encodeURIComponent excepts ignore slashes.
*/
secretary.core.encode_uri = (function encode_uri(uri){return clojure.string.join.cljs$core$IFn$_invoke$arity$2("/",cljs.core.map.cljs$core$IFn$_invoke$arity$2(secretary.core.encode,clojure.string.split.cljs$core$IFn$_invoke$arity$2(uri,/\//)));
});
secretary.core.decode = decodeURIComponent;
/**
* Parse a value from a serialized query-string key index. If the
* index value is empty 0 is returned, if it's a digit it returns the
* js/parseInt value, otherwise it returns the extracted index.
*/
secretary.core.parse_path = (function parse_path(path){var index_re = /\[([^\]]*)\]*/;var parts = cljs.core.re_seq(index_re,path);return cljs.core.map.cljs$core$IFn$_invoke$arity$2(((function (index_re,parts){
return (function (p__8871){var vec__8872 = p__8871;var _ = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8872,0,null);var part = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8872,1,null);if(cljs.core.empty_QMARK_(part))
{return 0;
} else
{if(cljs.core.truth_(cljs.core.re_matches(/\d+/,part)))
{return parseInt(part);
} else
{if(cljs.core.constant$keyword$6)
{return part;
} else
{return null;
}
}
}
});})(index_re,parts))
,parts);
});
/**
* Return a key path for a serialized query-string entry.
* 
* Ex.
* 
* (key-parse "foo[][a][][b]")
* ;; => ("foo" 0 "a" 0 "b")
* 
*/
secretary.core.key_parse = (function key_parse(k){var re = /([^\[\]]+)((?:\[[^\]]*\])*)?/;var vec__8874 = cljs.core.re_matches(re,k);var _ = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8874,0,null);var key = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8874,1,null);var path = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8874,2,null);var parsed_path = (cljs.core.truth_(path)?secretary.core.parse_path(path):null);return cljs.core.cons(key,parsed_path);
});
/**
* Like assoc-in but numbers in path create vectors instead of maps.
* 
* Ex.
* 
* (assoc-in-query-params {} ["foo" 0] 1)
* ;; => {"foo" [1]}
* 
* (assoc-in-query-params {} ["foo" 0 "a"] 1)
* ;; => {"foo" [{"a" 1}]}
* 
*/
secretary.core.assoc_in_query_params = (function assoc_in_query_params(m,path,v){var heads = (function (xs){return cljs.core.map_indexed((function (i,_){return cljs.core.take((i + 1),xs);
}),xs);
});var hs = heads(path);var m__$1 = cljs.core.reduce.cljs$core$IFn$_invoke$arity$3(((function (heads,hs){
return (function (m__$1,h){if((typeof cljs.core.last(h) === 'number') && (!(cljs.core.vector_QMARK_(cljs.core.get_in.cljs$core$IFn$_invoke$arity$2(m__$1,cljs.core.butlast(h))))))
{return cljs.core.assoc_in(m__$1,cljs.core.butlast(h),cljs.core.PersistentVector.EMPTY);
} else
{return m__$1;
}
});})(heads,hs))
,m,hs);if((cljs.core.last(path) === 0))
{return cljs.core.update_in.cljs$core$IFn$_invoke$arity$4(m__$1,cljs.core.butlast(path),cljs.core.conj,v);
} else
{return cljs.core.assoc_in(m__$1,path,v);
}
});
/**
* Extract a map of query parameters from a query string.
*/
secretary.core.decode_query_params = (function decode_query_params(query_string){var parts = clojure.string.split.cljs$core$IFn$_invoke$arity$2(query_string,/&/);var params = cljs.core.reduce.cljs$core$IFn$_invoke$arity$3(((function (parts){
return (function (m,part){var vec__8876 = clojure.string.split.cljs$core$IFn$_invoke$arity$3(part,/=/,2);var k = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8876,0,null);var v = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8876,1,null);return secretary.core.assoc_in_query_params(m,secretary.core.key_parse(k),(secretary.core.decode.cljs$core$IFn$_invoke$arity$1 ? secretary.core.decode.cljs$core$IFn$_invoke$arity$1(v) : secretary.core.decode.call(null,v)));
});})(parts))
,cljs.core.PersistentArrayMap.EMPTY,parts);var params__$1 = clojure.walk.keywordize_keys(params);return params__$1;
});
/**
* Like re-matches but result is a always vector. If re does not
* capture matches then it will return a vector of [m m] as if it had a
* single capture. Other wise it maintains consistent behavior with
* re-matches.
*/
secretary.core.re_matches_STAR_ = (function re_matches_STAR_(re,s){var ms = cljs.core.re_matches(re,s);if(cljs.core.truth_(ms))
{if(cljs.core.sequential_QMARK_(ms))
{return ms;
} else
{return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [ms,ms], null);
}
} else
{return null;
}
});
secretary.core.re_escape_chars = cljs.core.set("\\.*+|?()[]{}$^");
secretary.core.re_escape = (function re_escape(s){return cljs.core.reduce.cljs$core$IFn$_invoke$arity$3((function (s__$1,c){if(cljs.core.truth_((secretary.core.re_escape_chars.cljs$core$IFn$_invoke$arity$1 ? secretary.core.re_escape_chars.cljs$core$IFn$_invoke$arity$1(c) : secretary.core.re_escape_chars.call(null,c))))
{return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(s__$1)+"\\"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(c));
} else
{return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(s__$1)+cljs.core.str.cljs$core$IFn$_invoke$arity$1(c));
}
}),"",s);
});
/**
* Attempt to lex a single token from s with clauses. Each clause is a
* pair of [regexp action] where action is a function. regexp is
* expected to begin with ^ and contain a single capture. If the
* attempt is successful a vector of [s-without-token (action capture)]
* is returned. Otherwise the result is nil.
*/
secretary.core.lex_STAR_ = (function lex_STAR_(s,clauses){return cljs.core.some((function (p__8880){var vec__8881 = p__8880;var re = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8881,0,null);var action = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8881,1,null);var temp__4126__auto__ = cljs.core.re_find(re,s);if(cljs.core.truth_(temp__4126__auto__))
{var vec__8882 = temp__4126__auto__;var m = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8882,0,null);var c = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8882,1,null);return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.subs.cljs$core$IFn$_invoke$arity$2(s,cljs.core.count(m)),(action.cljs$core$IFn$_invoke$arity$1 ? action.cljs$core$IFn$_invoke$arity$1(c) : action.call(null,c))], null);
} else
{return null;
}
}),clauses);
});
/**
* Return a pair of [regex params]. regex is a compiled regular
* expression for matching routes. params is a list of route param
* names (:*, :id, etc.).
*/
secretary.core.lex_route = (function lex_route(s,clauses){var s__$1 = s;var pattern = "";var params = cljs.core.PersistentVector.EMPTY;while(true){
if(cljs.core.seq(s__$1))
{var vec__8885 = secretary.core.lex_STAR_(s__$1,clauses);var s__$2 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8885,0,null);var vec__8886 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8885,1,null);var r = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8886,0,null);var p = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8886,1,null);{
var G__8887 = s__$2;
var G__8888 = (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(pattern)+cljs.core.str.cljs$core$IFn$_invoke$arity$1(r));
var G__8889 = cljs.core.conj.cljs$core$IFn$_invoke$arity$2(params,p);
s__$1 = G__8887;
pattern = G__8888;
params = G__8889;
continue;
}
} else
{return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.re_pattern(("^"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(pattern)+"$")),cljs.core.remove(cljs.core.nil_QMARK_,params)], null);
}
break;
}
});
/**
* Given a route return an instance of IRouteMatches.
*/
secretary.core.compile_route = (function compile_route(orig_route){var clauses = new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [/^\*([^\s.:*\/]*)/,(function (v){var r = "(.*?)";var p = ((cljs.core.seq(v))?cljs.core.keyword.cljs$core$IFn$_invoke$arity$1(v):cljs.core.constant$keyword$105);return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [r,p], null);
})], null),new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [/^\:([^\s.:*\/]+)/,(function (v){var r = "([^,;?/]+)";var p = cljs.core.keyword.cljs$core$IFn$_invoke$arity$1(v);return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [r,p], null);
})], null),new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [/^([^:*]+)/,(function (v){var r = secretary.core.re_escape(v);return new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [r], null);
})], null)], null);var vec__8895 = secretary.core.lex_route(orig_route,clauses);var re = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8895,0,null);var params = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8895,1,null);if(typeof secretary.core.t8896 !== 'undefined')
{} else
{
/**
* @constructor
*/
secretary.core.t8896 = (function (params,re,vec__8895,clauses,orig_route,compile_route,meta8897){
this.params = params;
this.re = re;
this.vec__8895 = vec__8895;
this.clauses = clauses;
this.orig_route = orig_route;
this.compile_route = compile_route;
this.meta8897 = meta8897;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
secretary.core.t8896.cljs$lang$type = true;
secretary.core.t8896.cljs$lang$ctorStr = "secretary.core/t8896";
secretary.core.t8896.cljs$lang$ctorPrWriter = ((function (clauses,vec__8895,re,params){
return (function (this__4140__auto__,writer__4141__auto__,opt__4142__auto__){return cljs.core._write(writer__4141__auto__,"secretary.core/t8896");
});})(clauses,vec__8895,re,params))
;
secretary.core.t8896.prototype.secretary$core$IRouteMatches$ = true;
secretary.core.t8896.prototype.secretary$core$IRouteMatches$route_matches$arity$2 = ((function (clauses,vec__8895,re,params){
return (function (_,route){var self__ = this;
var ___$1 = this;var temp__4126__auto__ = secretary.core.re_matches_STAR_(self__.re,route);if(cljs.core.truth_(temp__4126__auto__))
{var vec__8899 = temp__4126__auto__;var ___$2 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8899,0,null);var ms = cljs.core.nthnext(vec__8899,1);return cljs.core.merge_with.cljs$core$IFn$_invoke$arity$variadic(cljs.core.vector,cljs.core.array_seq([cljs.core.PersistentArrayMap.EMPTY,cljs.core.partition.cljs$core$IFn$_invoke$arity$2(2,cljs.core.interleave.cljs$core$IFn$_invoke$arity$2(self__.params,cljs.core.map.cljs$core$IFn$_invoke$arity$2(secretary.core.decode,ms)))], 0));
} else
{return null;
}
});})(clauses,vec__8895,re,params))
;
secretary.core.t8896.prototype.secretary$core$IRouteValue$ = true;
secretary.core.t8896.prototype.secretary$core$IRouteValue$route_value$arity$1 = ((function (clauses,vec__8895,re,params){
return (function (this$){var self__ = this;
var this$__$1 = this;return self__.orig_route;
});})(clauses,vec__8895,re,params))
;
secretary.core.t8896.prototype.cljs$core$IMeta$_meta$arity$1 = ((function (clauses,vec__8895,re,params){
return (function (_8898){var self__ = this;
var _8898__$1 = this;return self__.meta8897;
});})(clauses,vec__8895,re,params))
;
secretary.core.t8896.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = ((function (clauses,vec__8895,re,params){
return (function (_8898,meta8897__$1){var self__ = this;
var _8898__$1 = this;return (new secretary.core.t8896(self__.params,self__.re,self__.vec__8895,self__.clauses,self__.orig_route,self__.compile_route,meta8897__$1));
});})(clauses,vec__8895,re,params))
;
secretary.core.__GT_t8896 = ((function (clauses,vec__8895,re,params){
return (function __GT_t8896(params__$1,re__$1,vec__8895__$1,clauses__$1,orig_route__$1,compile_route__$1,meta8897){return (new secretary.core.t8896(params__$1,re__$1,vec__8895__$1,clauses__$1,orig_route__$1,compile_route__$1,meta8897));
});})(clauses,vec__8895,re,params))
;
}
return (new secretary.core.t8896(params,re,vec__8895,clauses,orig_route,compile_route,null));
});
/**
* @param {...*} var_args
*/
secretary.core.render_route_STAR_ = (function() { 
var render_route_STAR___delegate = function (obj,args){if((function (){var G__8901 = obj;if(G__8901)
{var bit__4223__auto__ = null;if(cljs.core.truth_((function (){var or__3573__auto__ = bit__4223__auto__;if(cljs.core.truth_(or__3573__auto__))
{return or__3573__auto__;
} else
{return G__8901.secretary$core$IRenderRoute$;
}
})()))
{return true;
} else
{if((!G__8901.cljs$lang$protocol_mask$partition$))
{return cljs.core.native_satisfies_QMARK_(secretary.core.IRenderRoute,G__8901);
} else
{return false;
}
}
} else
{return cljs.core.native_satisfies_QMARK_(secretary.core.IRenderRoute,G__8901);
}
})())
{return cljs.core.apply.cljs$core$IFn$_invoke$arity$3(secretary.core.render_route,obj,args);
} else
{return null;
}
};
var render_route_STAR_ = function (obj,var_args){
var args = null;if (arguments.length > 1) {
  args = cljs.core.array_seq(Array.prototype.slice.call(arguments, 1),0);} 
return render_route_STAR___delegate.call(this,obj,args);};
render_route_STAR_.cljs$lang$maxFixedArity = 1;
render_route_STAR_.cljs$lang$applyTo = (function (arglist__8902){
var obj = cljs.core.first(arglist__8902);
var args = cljs.core.rest(arglist__8902);
return render_route_STAR___delegate(obj,args);
});
render_route_STAR_.cljs$core$IFn$_invoke$arity$variadic = render_route_STAR___delegate;
return render_route_STAR_;
})()
;
secretary.core._STAR_routes_STAR_ = cljs.core.atom.cljs$core$IFn$_invoke$arity$1(cljs.core.PersistentVector.EMPTY);
secretary.core.add_route_BANG_ = (function add_route_BANG_(obj,action){var obj__$1 = ((typeof obj === 'string')?secretary.core.compile_route(obj):obj);return cljs.core.swap_BANG_.cljs$core$IFn$_invoke$arity$3(secretary.core._STAR_routes_STAR_,cljs.core.conj,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [obj__$1,action], null));
});
secretary.core.remove_route_BANG_ = (function remove_route_BANG_(obj){return cljs.core.swap_BANG_.cljs$core$IFn$_invoke$arity$2(secretary.core._STAR_routes_STAR_,(function (rs){return cljs.core.filterv((function (p__8905){var vec__8906 = p__8905;var x = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8906,0,null);var _ = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8906,1,null);return cljs.core.not_EQ_.cljs$core$IFn$_invoke$arity$2(x,obj);
}),rs);
}));
});
secretary.core.reset_routes_BANG_ = (function reset_routes_BANG_(){return cljs.core.reset_BANG_(secretary.core._STAR_routes_STAR_,cljs.core.PersistentVector.EMPTY);
});
secretary.core.locate_route = (function locate_route(route){return cljs.core.some((function (p__8909){var vec__8910 = p__8909;var compiled_route = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8910,0,null);var action = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8910,1,null);var temp__4126__auto__ = secretary.core.route_matches(compiled_route,route);if(cljs.core.truth_(temp__4126__auto__))
{var params = temp__4126__auto__;return new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$60,action,cljs.core.constant$keyword$106,params,cljs.core.constant$keyword$107,compiled_route], null);
} else
{return null;
}
}),cljs.core.deref(secretary.core._STAR_routes_STAR_));
});
/**
* Returns original route value as set in defroute when passed a URI path.
*/
secretary.core.locate_route_value = (function locate_route_value(uri){return secretary.core.route_value(cljs.core.constant$keyword$107.cljs$core$IFn$_invoke$arity$1(secretary.core.locate_route(uri)));
});
secretary.core.prefix = (function prefix(){return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(secretary.core.get_config(new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$101], null))));
});
secretary.core.uri_without_prefix = (function uri_without_prefix(uri){return clojure.string.replace(uri,cljs.core.re_pattern(("^"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(secretary.core.prefix()))),"");
});
/**
* Ensures that the uri has a leading slash
*/
secretary.core.uri_with_leading_slash = (function uri_with_leading_slash(uri){if(cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2("/",cljs.core.first(uri)))
{return uri;
} else
{return ("/"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(uri));
}
});
/**
* Dispatch an action for a given route if it matches the URI path.
*/
secretary.core.dispatch_BANG_ = (function dispatch_BANG_(uri){var vec__8913 = clojure.string.split.cljs$core$IFn$_invoke$arity$2(secretary.core.uri_without_prefix(uri),/\?/);var uri_path = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8913,0,null);var query_string = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8913,1,null);var uri_path__$1 = secretary.core.uri_with_leading_slash(uri_path);var query_params = (cljs.core.truth_(query_string)?new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$108,secretary.core.decode_query_params(query_string)], null):null);var map__8914 = secretary.core.locate_route(uri_path__$1);var map__8914__$1 = ((cljs.core.seq_QMARK_(map__8914))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__8914):map__8914);var params = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__8914__$1,cljs.core.constant$keyword$106);var action = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__8914__$1,cljs.core.constant$keyword$60);var action__$1 = (function (){var or__3573__auto__ = action;if(cljs.core.truth_(or__3573__auto__))
{return or__3573__auto__;
} else
{return cljs.core.identity;
}
})();var params__$1 = cljs.core.merge.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([params,query_params], 0));return (action__$1.cljs$core$IFn$_invoke$arity$1 ? action__$1.cljs$core$IFn$_invoke$arity$1(params__$1) : action__$1.call(null,params__$1));
});
secretary.core.invalid_params = (function invalid_params(params,validations){return cljs.core.reduce.cljs$core$IFn$_invoke$arity$3((function (m,p__8917){var vec__8918 = p__8917;var key = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8918,0,null);var validation = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8918,1,null);var value = cljs.core.get.cljs$core$IFn$_invoke$arity$2(params,key);if(cljs.core.truth_(cljs.core.re_matches(validation,value)))
{return m;
} else
{return cljs.core.assoc.cljs$core$IFn$_invoke$arity$3(m,key,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [value,validation], null));
}
}),cljs.core.PersistentArrayMap.EMPTY,cljs.core.partition.cljs$core$IFn$_invoke$arity$2(2,validations));
});
secretary.core.params_valid_QMARK_ = (function params_valid_QMARK_(params,validations){return cljs.core.empty_QMARK_(secretary.core.invalid_params(params,validations));
});
cljs.core.PersistentVector.prototype.secretary$core$IRouteMatches$ = true;
cljs.core.PersistentVector.prototype.secretary$core$IRouteMatches$route_matches$arity$2 = (function (p__8919,route){var vec__8920 = p__8919;var route_string = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8920,0,null);var validations = cljs.core.nthnext(vec__8920,1);var vec__8921 = this;var route_string__$1 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8921,0,null);var validations__$1 = cljs.core.nthnext(vec__8921,1);var params = secretary.core.compile_route(route_string__$1).secretary$core$IRouteMatches$route_matches$arity$2(null,route);if(secretary.core.params_valid_QMARK_(params,validations__$1))
{return params;
} else
{return null;
}
});
RegExp.prototype.secretary$core$IRouteMatches$ = true;
RegExp.prototype.secretary$core$IRouteMatches$route_matches$arity$2 = (function (this$,route){var this$__$1 = this;var temp__4126__auto__ = secretary.core.re_matches_STAR_(this$__$1,route);if(cljs.core.truth_(temp__4126__auto__))
{var vec__8922 = temp__4126__auto__;var _ = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8922,0,null);var ms = cljs.core.nthnext(vec__8922,1);return cljs.core.vec(ms);
} else
{return null;
}
});
(secretary.core.IRouteMatches["string"] = true);
(secretary.core.route_matches["string"] = (function (this$,route){return secretary.core.compile_route(this$).secretary$core$IRouteMatches$route_matches$arity$2(null,route);
}));
cljs.core.PersistentVector.prototype.secretary$core$IRouteValue$ = true;
cljs.core.PersistentVector.prototype.secretary$core$IRouteValue$route_value$arity$1 = (function (p__8923){var vec__8924 = p__8923;var route_string = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8924,0,null);var validations = cljs.core.nthnext(vec__8924,1);var vec__8925 = this;var route_string__$1 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8925,0,null);var validations__$1 = cljs.core.nthnext(vec__8925,1);return cljs.core.vec(cljs.core.cons(secretary.core.route_value(route_string__$1),validations__$1));
});
RegExp.prototype.secretary$core$IRouteValue$ = true;
RegExp.prototype.secretary$core$IRouteValue$route_value$arity$1 = (function (this$){var this$__$1 = this;return this$__$1;
});
(secretary.core.IRouteValue["string"] = true);
(secretary.core.route_value["string"] = (function (this$){return secretary.core.compile_route(this$).secretary$core$IRouteValue$route_value$arity$1(null);
}));
cljs.core.PersistentVector.prototype.secretary$core$IRenderRoute$ = true;
cljs.core.PersistentVector.prototype.secretary$core$IRenderRoute$render_route$arity$1 = (function (this$){var this$__$1 = this;return secretary.core.render_route.cljs$core$IFn$_invoke$arity$2(this$__$1,cljs.core.PersistentArrayMap.EMPTY);
});
cljs.core.PersistentVector.prototype.secretary$core$IRenderRoute$render_route$arity$2 = (function (p__8926,params){var vec__8927 = p__8926;var route_string = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8927,0,null);var validations = cljs.core.nthnext(vec__8927,1);var vec__8928 = this;var route_string__$1 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8928,0,null);var validations__$1 = cljs.core.nthnext(vec__8928,1);var invalid = secretary.core.invalid_params(params,validations__$1);if(cljs.core.empty_QMARK_(invalid))
{return secretary.core.render_route.cljs$core$IFn$_invoke$arity$2(route_string__$1,params);
} else
{throw cljs.core.ex_info.cljs$core$IFn$_invoke$arity$2("Could not build route: invalid params",invalid);
}
});
(secretary.core.IRenderRoute["string"] = true);
(secretary.core.render_route["string"] = (function (this$){return secretary.core.render_route.cljs$core$IFn$_invoke$arity$2(this$,cljs.core.PersistentArrayMap.EMPTY);
}));
(secretary.core.render_route["string"] = (function (this$,params){var map__8929 = params;var map__8929__$1 = ((cljs.core.seq_QMARK_(map__8929))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__8929):map__8929);var m = map__8929__$1;var query_params = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__8929__$1,cljs.core.constant$keyword$108);var a = cljs.core.atom.cljs$core$IFn$_invoke$arity$1(m);var path = this$.replace((new RegExp(":[^\\s.:*/]+|\\*[^\\s.:*/]*","g")),((function (map__8929,map__8929__$1,m,query_params,a){
return (function ($1){var lookup = cljs.core.keyword.cljs$core$IFn$_invoke$arity$1(((cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2($1,"*"))?$1:cljs.core.subs.cljs$core$IFn$_invoke$arity$2($1,1)));var v = cljs.core.get.cljs$core$IFn$_invoke$arity$2(cljs.core.deref(a),lookup);var replacement = ((cljs.core.sequential_QMARK_(v))?(function (){cljs.core.swap_BANG_.cljs$core$IFn$_invoke$arity$4(a,cljs.core.assoc,lookup,cljs.core.next(v));
return secretary.core.encode_uri(cljs.core.first(v));
})():(cljs.core.truth_(v)?secretary.core.encode_uri(v):$1));return replacement;
});})(map__8929,map__8929__$1,m,query_params,a))
);var path__$1 = (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(secretary.core.get_config(new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$101], null)))+cljs.core.str.cljs$core$IFn$_invoke$arity$1(path));var temp__4124__auto__ = (function (){var and__3561__auto__ = query_params;if(cljs.core.truth_(and__3561__auto__))
{return secretary.core.encode_query_params(query_params);
} else
{return and__3561__auto__;
}
})();if(cljs.core.truth_(temp__4124__auto__))
{var query_string = temp__4124__auto__;return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(path__$1)+"?"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(query_string));
} else
{return path__$1;
}
}));
