// Compiled by ClojureScript 0.0-2234
goog.provide('sablono.core');
goog.require('cljs.core');
goog.require('clojure.walk');
goog.require('clojure.string');
goog.require('sablono.util');
goog.require('goog.dom');
goog.require('goog.dom');
goog.require('sablono.interpreter');
goog.require('sablono.interpreter');
goog.require('sablono.util');
goog.require('clojure.walk');
goog.require('clojure.string');
/**
* Add an optional attribute argument to a function that returns a element vector.
*/
sablono.core.wrap_attrs = (function wrap_attrs(func){return (function() { 
var G__8342__delegate = function (args){if(cljs.core.map_QMARK_(cljs.core.first(args)))
{var vec__8341 = cljs.core.apply.cljs$core$IFn$_invoke$arity$2(func,cljs.core.rest(args));var tag = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8341,0,null);var body = cljs.core.nthnext(vec__8341,1);if(cljs.core.map_QMARK_(cljs.core.first(body)))
{return cljs.core.apply.cljs$core$IFn$_invoke$arity$4(cljs.core.vector,tag,cljs.core.merge.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([cljs.core.first(body),cljs.core.first(args)], 0)),cljs.core.rest(body));
} else
{return cljs.core.apply.cljs$core$IFn$_invoke$arity$4(cljs.core.vector,tag,cljs.core.first(args),body);
}
} else
{return cljs.core.apply.cljs$core$IFn$_invoke$arity$2(func,args);
}
};
var G__8342 = function (var_args){
var args = null;if (arguments.length > 0) {
  args = cljs.core.array_seq(Array.prototype.slice.call(arguments, 0),0);} 
return G__8342__delegate.call(this,args);};
G__8342.cljs$lang$maxFixedArity = 0;
G__8342.cljs$lang$applyTo = (function (arglist__8343){
var args = cljs.core.seq(arglist__8343);
return G__8342__delegate(args);
});
G__8342.cljs$core$IFn$_invoke$arity$variadic = G__8342__delegate;
return G__8342;
})()
;
});
sablono.core.update_arglists = (function update_arglists(arglists){var iter__4298__auto__ = (function iter__8348(s__8349){return (new cljs.core.LazySeq(null,(function (){var s__8349__$1 = s__8349;while(true){
var temp__4126__auto__ = cljs.core.seq(s__8349__$1);if(temp__4126__auto__)
{var s__8349__$2 = temp__4126__auto__;if(cljs.core.chunked_seq_QMARK_(s__8349__$2))
{var c__4296__auto__ = cljs.core.chunk_first(s__8349__$2);var size__4297__auto__ = cljs.core.count(c__4296__auto__);var b__8351 = cljs.core.chunk_buffer(size__4297__auto__);if((function (){var i__8350 = 0;while(true){
if((i__8350 < size__4297__auto__))
{var args = cljs.core._nth.cljs$core$IFn$_invoke$arity$2(c__4296__auto__,i__8350);cljs.core.chunk_append(b__8351,cljs.core.vec(cljs.core.cons(new cljs.core.Symbol(null,"attr-map?","attr-map?",-1682549128,null),args)));
{
var G__8352 = (i__8350 + 1);
i__8350 = G__8352;
continue;
}
} else
{return true;
}
break;
}
})())
{return cljs.core.chunk_cons(cljs.core.chunk(b__8351),iter__8348(cljs.core.chunk_rest(s__8349__$2)));
} else
{return cljs.core.chunk_cons(cljs.core.chunk(b__8351),null);
}
} else
{var args = cljs.core.first(s__8349__$2);return cljs.core.cons(cljs.core.vec(cljs.core.cons(new cljs.core.Symbol(null,"attr-map?","attr-map?",-1682549128,null),args)),iter__8348(cljs.core.rest(s__8349__$2)));
}
} else
{return null;
}
break;
}
}),null,null));
});return iter__4298__auto__(arglists);
});
/**
* Render the React `component` as an HTML string.
*/
sablono.core.render = (function render(component){return React.renderComponentToString(component);
});
/**
* Include a list of external stylesheet files.
* @param {...*} var_args
*/
sablono.core.include_css = (function() { 
var include_css__delegate = function (styles){var iter__4298__auto__ = (function iter__8357(s__8358){return (new cljs.core.LazySeq(null,(function (){var s__8358__$1 = s__8358;while(true){
var temp__4126__auto__ = cljs.core.seq(s__8358__$1);if(temp__4126__auto__)
{var s__8358__$2 = temp__4126__auto__;if(cljs.core.chunked_seq_QMARK_(s__8358__$2))
{var c__4296__auto__ = cljs.core.chunk_first(s__8358__$2);var size__4297__auto__ = cljs.core.count(c__4296__auto__);var b__8360 = cljs.core.chunk_buffer(size__4297__auto__);if((function (){var i__8359 = 0;while(true){
if((i__8359 < size__4297__auto__))
{var style = cljs.core._nth.cljs$core$IFn$_invoke$arity$2(c__4296__auto__,i__8359);cljs.core.chunk_append(b__8360,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$37,new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$38,"text/css",cljs.core.constant$keyword$39,sablono.util.as_str.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([style], 0)),cljs.core.constant$keyword$40,"stylesheet"], null)], null));
{
var G__8361 = (i__8359 + 1);
i__8359 = G__8361;
continue;
}
} else
{return true;
}
break;
}
})())
{return cljs.core.chunk_cons(cljs.core.chunk(b__8360),iter__8357(cljs.core.chunk_rest(s__8358__$2)));
} else
{return cljs.core.chunk_cons(cljs.core.chunk(b__8360),null);
}
} else
{var style = cljs.core.first(s__8358__$2);return cljs.core.cons(new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$37,new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$38,"text/css",cljs.core.constant$keyword$39,sablono.util.as_str.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([style], 0)),cljs.core.constant$keyword$40,"stylesheet"], null)], null),iter__8357(cljs.core.rest(s__8358__$2)));
}
} else
{return null;
}
break;
}
}),null,null));
});return iter__4298__auto__(styles);
};
var include_css = function (var_args){
var styles = null;if (arguments.length > 0) {
  styles = cljs.core.array_seq(Array.prototype.slice.call(arguments, 0),0);} 
return include_css__delegate.call(this,styles);};
include_css.cljs$lang$maxFixedArity = 0;
include_css.cljs$lang$applyTo = (function (arglist__8362){
var styles = cljs.core.seq(arglist__8362);
return include_css__delegate(styles);
});
include_css.cljs$core$IFn$_invoke$arity$variadic = include_css__delegate;
return include_css;
})()
;
/**
* Include the JavaScript library at `src`.
*/
sablono.core.include_js = (function include_js(src){return goog.dom.appendChild(goog.dom.getDocument().body,goog.dom.createDom("script",{"src": src}));
});
/**
* Include Facebook's React JavaScript library.
*/
sablono.core.include_react = (function include_react(){return sablono.core.include_js("http://fb.me/react-0.9.0.js");
});
/**
* Wraps some content in a HTML hyperlink with the supplied URL.
* @param {...*} var_args
*/
sablono.core.link_to8363 = (function() { 
var link_to8363__delegate = function (url,content){return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$41,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$39,sablono.util.as_str.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([url], 0))], null),content], null);
};
var link_to8363 = function (url,var_args){
var content = null;if (arguments.length > 1) {
  content = cljs.core.array_seq(Array.prototype.slice.call(arguments, 1),0);} 
return link_to8363__delegate.call(this,url,content);};
link_to8363.cljs$lang$maxFixedArity = 1;
link_to8363.cljs$lang$applyTo = (function (arglist__8364){
var url = cljs.core.first(arglist__8364);
var content = cljs.core.rest(arglist__8364);
return link_to8363__delegate(url,content);
});
link_to8363.cljs$core$IFn$_invoke$arity$variadic = link_to8363__delegate;
return link_to8363;
})()
;
sablono.core.link_to = sablono.core.wrap_attrs(sablono.core.link_to8363);
/**
* Wraps some content in a HTML hyperlink with the supplied e-mail
* address. If no content provided use the e-mail address as content.
* @param {...*} var_args
*/
sablono.core.mail_to8365 = (function() { 
var mail_to8365__delegate = function (e_mail,p__8366){var vec__8368 = p__8366;var content = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8368,0,null);return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$41,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$39,("mailto:"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(e_mail))], null),(function (){var or__3573__auto__ = content;if(cljs.core.truth_(or__3573__auto__))
{return or__3573__auto__;
} else
{return e_mail;
}
})()], null);
};
var mail_to8365 = function (e_mail,var_args){
var p__8366 = null;if (arguments.length > 1) {
  p__8366 = cljs.core.array_seq(Array.prototype.slice.call(arguments, 1),0);} 
return mail_to8365__delegate.call(this,e_mail,p__8366);};
mail_to8365.cljs$lang$maxFixedArity = 1;
mail_to8365.cljs$lang$applyTo = (function (arglist__8369){
var e_mail = cljs.core.first(arglist__8369);
var p__8366 = cljs.core.rest(arglist__8369);
return mail_to8365__delegate(e_mail,p__8366);
});
mail_to8365.cljs$core$IFn$_invoke$arity$variadic = mail_to8365__delegate;
return mail_to8365;
})()
;
sablono.core.mail_to = sablono.core.wrap_attrs(sablono.core.mail_to8365);
/**
* Wrap a collection in an unordered list.
*/
sablono.core.unordered_list8370 = (function unordered_list8370(coll){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$42,(function (){var iter__4298__auto__ = (function iter__8375(s__8376){return (new cljs.core.LazySeq(null,(function (){var s__8376__$1 = s__8376;while(true){
var temp__4126__auto__ = cljs.core.seq(s__8376__$1);if(temp__4126__auto__)
{var s__8376__$2 = temp__4126__auto__;if(cljs.core.chunked_seq_QMARK_(s__8376__$2))
{var c__4296__auto__ = cljs.core.chunk_first(s__8376__$2);var size__4297__auto__ = cljs.core.count(c__4296__auto__);var b__8378 = cljs.core.chunk_buffer(size__4297__auto__);if((function (){var i__8377 = 0;while(true){
if((i__8377 < size__4297__auto__))
{var x = cljs.core._nth.cljs$core$IFn$_invoke$arity$2(c__4296__auto__,i__8377);cljs.core.chunk_append(b__8378,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$43,x], null));
{
var G__8379 = (i__8377 + 1);
i__8377 = G__8379;
continue;
}
} else
{return true;
}
break;
}
})())
{return cljs.core.chunk_cons(cljs.core.chunk(b__8378),iter__8375(cljs.core.chunk_rest(s__8376__$2)));
} else
{return cljs.core.chunk_cons(cljs.core.chunk(b__8378),null);
}
} else
{var x = cljs.core.first(s__8376__$2);return cljs.core.cons(new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$43,x], null),iter__8375(cljs.core.rest(s__8376__$2)));
}
} else
{return null;
}
break;
}
}),null,null));
});return iter__4298__auto__(coll);
})()], null);
});
sablono.core.unordered_list = sablono.core.wrap_attrs(sablono.core.unordered_list8370);
/**
* Wrap a collection in an ordered list.
*/
sablono.core.ordered_list8380 = (function ordered_list8380(coll){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$44,(function (){var iter__4298__auto__ = (function iter__8385(s__8386){return (new cljs.core.LazySeq(null,(function (){var s__8386__$1 = s__8386;while(true){
var temp__4126__auto__ = cljs.core.seq(s__8386__$1);if(temp__4126__auto__)
{var s__8386__$2 = temp__4126__auto__;if(cljs.core.chunked_seq_QMARK_(s__8386__$2))
{var c__4296__auto__ = cljs.core.chunk_first(s__8386__$2);var size__4297__auto__ = cljs.core.count(c__4296__auto__);var b__8388 = cljs.core.chunk_buffer(size__4297__auto__);if((function (){var i__8387 = 0;while(true){
if((i__8387 < size__4297__auto__))
{var x = cljs.core._nth.cljs$core$IFn$_invoke$arity$2(c__4296__auto__,i__8387);cljs.core.chunk_append(b__8388,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$43,x], null));
{
var G__8389 = (i__8387 + 1);
i__8387 = G__8389;
continue;
}
} else
{return true;
}
break;
}
})())
{return cljs.core.chunk_cons(cljs.core.chunk(b__8388),iter__8385(cljs.core.chunk_rest(s__8386__$2)));
} else
{return cljs.core.chunk_cons(cljs.core.chunk(b__8388),null);
}
} else
{var x = cljs.core.first(s__8386__$2);return cljs.core.cons(new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$43,x], null),iter__8385(cljs.core.rest(s__8386__$2)));
}
} else
{return null;
}
break;
}
}),null,null));
});return iter__4298__auto__(coll);
})()], null);
});
sablono.core.ordered_list = sablono.core.wrap_attrs(sablono.core.ordered_list8380);
/**
* Create an image element.
*/
sablono.core.image8390 = (function() {
var image8390 = null;
var image8390__1 = (function (src){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$45,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$46,sablono.util.as_str.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([src], 0))], null)], null);
});
var image8390__2 = (function (src,alt){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$45,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$46,sablono.util.as_str.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([src], 0)),cljs.core.constant$keyword$47,alt], null)], null);
});
image8390 = function(src,alt){
switch(arguments.length){
case 1:
return image8390__1.call(this,src);
case 2:
return image8390__2.call(this,src,alt);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
image8390.cljs$core$IFn$_invoke$arity$1 = image8390__1;
image8390.cljs$core$IFn$_invoke$arity$2 = image8390__2;
return image8390;
})()
;
sablono.core.image = sablono.core.wrap_attrs(sablono.core.image8390);
sablono.core._STAR_group_STAR_ = cljs.core.PersistentVector.EMPTY;
/**
* Create a field name from the supplied argument the current field group.
*/
sablono.core.make_name = (function make_name(name){return cljs.core.reduce.cljs$core$IFn$_invoke$arity$2((function (p1__8391_SHARP_,p2__8392_SHARP_){return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(p1__8391_SHARP_)+"["+cljs.core.str.cljs$core$IFn$_invoke$arity$1(p2__8392_SHARP_)+"]");
}),cljs.core.conj.cljs$core$IFn$_invoke$arity$2(sablono.core._STAR_group_STAR_,sablono.util.as_str.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([name], 0))));
});
/**
* Create a field id from the supplied argument and current field group.
*/
sablono.core.make_id = (function make_id(name){return cljs.core.reduce.cljs$core$IFn$_invoke$arity$2((function (p1__8393_SHARP_,p2__8394_SHARP_){return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(p1__8393_SHARP_)+"-"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(p2__8394_SHARP_));
}),cljs.core.conj.cljs$core$IFn$_invoke$arity$2(sablono.core._STAR_group_STAR_,sablono.util.as_str.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([name], 0))));
});
/**
* Creates a new <input> element.
*/
sablono.core.input_field_STAR_ = (function input_field_STAR_(type,name,value){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$36,new cljs.core.PersistentArrayMap(null, 4, [cljs.core.constant$keyword$38,type,cljs.core.constant$keyword$48,sablono.core.make_name(name),cljs.core.constant$keyword$34,sablono.core.make_id(name),cljs.core.constant$keyword$11,value], null)], null);
});
/**
* Creates a color input field.
*/
sablono.core.color_field8395 = (function() {
var color_field8395 = null;
var color_field8395__1 = (function (name__5778__auto__){return color_field8395.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var color_field8395__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"color","color",-1545688804,null))),name__5778__auto__,value__5779__auto__);
});
color_field8395 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return color_field8395__1.call(this,name__5778__auto__);
case 2:
return color_field8395__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
color_field8395.cljs$core$IFn$_invoke$arity$1 = color_field8395__1;
color_field8395.cljs$core$IFn$_invoke$arity$2 = color_field8395__2;
return color_field8395;
})()
;
sablono.core.color_field = sablono.core.wrap_attrs(sablono.core.color_field8395);
/**
* Creates a date input field.
*/
sablono.core.date_field8396 = (function() {
var date_field8396 = null;
var date_field8396__1 = (function (name__5778__auto__){return date_field8396.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var date_field8396__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"date","date",-1637455513,null))),name__5778__auto__,value__5779__auto__);
});
date_field8396 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return date_field8396__1.call(this,name__5778__auto__);
case 2:
return date_field8396__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
date_field8396.cljs$core$IFn$_invoke$arity$1 = date_field8396__1;
date_field8396.cljs$core$IFn$_invoke$arity$2 = date_field8396__2;
return date_field8396;
})()
;
sablono.core.date_field = sablono.core.wrap_attrs(sablono.core.date_field8396);
/**
* Creates a datetime input field.
*/
sablono.core.datetime_field8397 = (function() {
var datetime_field8397 = null;
var datetime_field8397__1 = (function (name__5778__auto__){return datetime_field8397.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var datetime_field8397__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"datetime","datetime",153171252,null))),name__5778__auto__,value__5779__auto__);
});
datetime_field8397 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return datetime_field8397__1.call(this,name__5778__auto__);
case 2:
return datetime_field8397__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
datetime_field8397.cljs$core$IFn$_invoke$arity$1 = datetime_field8397__1;
datetime_field8397.cljs$core$IFn$_invoke$arity$2 = datetime_field8397__2;
return datetime_field8397;
})()
;
sablono.core.datetime_field = sablono.core.wrap_attrs(sablono.core.datetime_field8397);
/**
* Creates a datetime-local input field.
*/
sablono.core.datetime_local_field8398 = (function() {
var datetime_local_field8398 = null;
var datetime_local_field8398__1 = (function (name__5778__auto__){return datetime_local_field8398.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var datetime_local_field8398__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"datetime-local","datetime-local",1631019090,null))),name__5778__auto__,value__5779__auto__);
});
datetime_local_field8398 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return datetime_local_field8398__1.call(this,name__5778__auto__);
case 2:
return datetime_local_field8398__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
datetime_local_field8398.cljs$core$IFn$_invoke$arity$1 = datetime_local_field8398__1;
datetime_local_field8398.cljs$core$IFn$_invoke$arity$2 = datetime_local_field8398__2;
return datetime_local_field8398;
})()
;
sablono.core.datetime_local_field = sablono.core.wrap_attrs(sablono.core.datetime_local_field8398);
/**
* Creates a email input field.
*/
sablono.core.email_field8399 = (function() {
var email_field8399 = null;
var email_field8399__1 = (function (name__5778__auto__){return email_field8399.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var email_field8399__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"email","email",-1543912107,null))),name__5778__auto__,value__5779__auto__);
});
email_field8399 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return email_field8399__1.call(this,name__5778__auto__);
case 2:
return email_field8399__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
email_field8399.cljs$core$IFn$_invoke$arity$1 = email_field8399__1;
email_field8399.cljs$core$IFn$_invoke$arity$2 = email_field8399__2;
return email_field8399;
})()
;
sablono.core.email_field = sablono.core.wrap_attrs(sablono.core.email_field8399);
/**
* Creates a file input field.
*/
sablono.core.file_field8400 = (function() {
var file_field8400 = null;
var file_field8400__1 = (function (name__5778__auto__){return file_field8400.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var file_field8400__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"file","file",-1637388491,null))),name__5778__auto__,value__5779__auto__);
});
file_field8400 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return file_field8400__1.call(this,name__5778__auto__);
case 2:
return file_field8400__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
file_field8400.cljs$core$IFn$_invoke$arity$1 = file_field8400__1;
file_field8400.cljs$core$IFn$_invoke$arity$2 = file_field8400__2;
return file_field8400;
})()
;
sablono.core.file_field = sablono.core.wrap_attrs(sablono.core.file_field8400);
/**
* Creates a hidden input field.
*/
sablono.core.hidden_field8401 = (function() {
var hidden_field8401 = null;
var hidden_field8401__1 = (function (name__5778__auto__){return hidden_field8401.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var hidden_field8401__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"hidden","hidden",1436948323,null))),name__5778__auto__,value__5779__auto__);
});
hidden_field8401 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return hidden_field8401__1.call(this,name__5778__auto__);
case 2:
return hidden_field8401__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
hidden_field8401.cljs$core$IFn$_invoke$arity$1 = hidden_field8401__1;
hidden_field8401.cljs$core$IFn$_invoke$arity$2 = hidden_field8401__2;
return hidden_field8401;
})()
;
sablono.core.hidden_field = sablono.core.wrap_attrs(sablono.core.hidden_field8401);
/**
* Creates a month input field.
*/
sablono.core.month_field8402 = (function() {
var month_field8402 = null;
var month_field8402__1 = (function (name__5778__auto__){return month_field8402.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var month_field8402__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"month","month",-1536451527,null))),name__5778__auto__,value__5779__auto__);
});
month_field8402 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return month_field8402__1.call(this,name__5778__auto__);
case 2:
return month_field8402__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
month_field8402.cljs$core$IFn$_invoke$arity$1 = month_field8402__1;
month_field8402.cljs$core$IFn$_invoke$arity$2 = month_field8402__2;
return month_field8402;
})()
;
sablono.core.month_field = sablono.core.wrap_attrs(sablono.core.month_field8402);
/**
* Creates a number input field.
*/
sablono.core.number_field8403 = (function() {
var number_field8403 = null;
var number_field8403__1 = (function (name__5778__auto__){return number_field8403.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var number_field8403__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"number","number",1620071682,null))),name__5778__auto__,value__5779__auto__);
});
number_field8403 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return number_field8403__1.call(this,name__5778__auto__);
case 2:
return number_field8403__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
number_field8403.cljs$core$IFn$_invoke$arity$1 = number_field8403__1;
number_field8403.cljs$core$IFn$_invoke$arity$2 = number_field8403__2;
return number_field8403;
})()
;
sablono.core.number_field = sablono.core.wrap_attrs(sablono.core.number_field8403);
/**
* Creates a password input field.
*/
sablono.core.password_field8404 = (function() {
var password_field8404 = null;
var password_field8404__1 = (function (name__5778__auto__){return password_field8404.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var password_field8404__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"password","password",-423545772,null))),name__5778__auto__,value__5779__auto__);
});
password_field8404 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return password_field8404__1.call(this,name__5778__auto__);
case 2:
return password_field8404__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
password_field8404.cljs$core$IFn$_invoke$arity$1 = password_field8404__1;
password_field8404.cljs$core$IFn$_invoke$arity$2 = password_field8404__2;
return password_field8404;
})()
;
sablono.core.password_field = sablono.core.wrap_attrs(sablono.core.password_field8404);
/**
* Creates a range input field.
*/
sablono.core.range_field8405 = (function() {
var range_field8405 = null;
var range_field8405__1 = (function (name__5778__auto__){return range_field8405.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var range_field8405__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"range","range",-1532251402,null))),name__5778__auto__,value__5779__auto__);
});
range_field8405 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return range_field8405__1.call(this,name__5778__auto__);
case 2:
return range_field8405__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
range_field8405.cljs$core$IFn$_invoke$arity$1 = range_field8405__1;
range_field8405.cljs$core$IFn$_invoke$arity$2 = range_field8405__2;
return range_field8405;
})()
;
sablono.core.range_field = sablono.core.wrap_attrs(sablono.core.range_field8405);
/**
* Creates a search input field.
*/
sablono.core.search_field8406 = (function() {
var search_field8406 = null;
var search_field8406__1 = (function (name__5778__auto__){return search_field8406.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var search_field8406__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"search","search",1748098913,null))),name__5778__auto__,value__5779__auto__);
});
search_field8406 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return search_field8406__1.call(this,name__5778__auto__);
case 2:
return search_field8406__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
search_field8406.cljs$core$IFn$_invoke$arity$1 = search_field8406__1;
search_field8406.cljs$core$IFn$_invoke$arity$2 = search_field8406__2;
return search_field8406;
})()
;
sablono.core.search_field = sablono.core.wrap_attrs(sablono.core.search_field8406);
/**
* Creates a tel input field.
*/
sablono.core.tel_field8407 = (function() {
var tel_field8407 = null;
var tel_field8407__1 = (function (name__5778__auto__){return tel_field8407.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var tel_field8407__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"tel","tel",-1640416812,null))),name__5778__auto__,value__5779__auto__);
});
tel_field8407 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return tel_field8407__1.call(this,name__5778__auto__);
case 2:
return tel_field8407__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
tel_field8407.cljs$core$IFn$_invoke$arity$1 = tel_field8407__1;
tel_field8407.cljs$core$IFn$_invoke$arity$2 = tel_field8407__2;
return tel_field8407;
})()
;
sablono.core.tel_field = sablono.core.wrap_attrs(sablono.core.tel_field8407);
/**
* Creates a text input field.
*/
sablono.core.text_field8408 = (function() {
var text_field8408 = null;
var text_field8408__1 = (function (name__5778__auto__){return text_field8408.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var text_field8408__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"text","text",-1636974874,null))),name__5778__auto__,value__5779__auto__);
});
text_field8408 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return text_field8408__1.call(this,name__5778__auto__);
case 2:
return text_field8408__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
text_field8408.cljs$core$IFn$_invoke$arity$1 = text_field8408__1;
text_field8408.cljs$core$IFn$_invoke$arity$2 = text_field8408__2;
return text_field8408;
})()
;
sablono.core.text_field = sablono.core.wrap_attrs(sablono.core.text_field8408);
/**
* Creates a time input field.
*/
sablono.core.time_field8409 = (function() {
var time_field8409 = null;
var time_field8409__1 = (function (name__5778__auto__){return time_field8409.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var time_field8409__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"time","time",-1636971386,null))),name__5778__auto__,value__5779__auto__);
});
time_field8409 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return time_field8409__1.call(this,name__5778__auto__);
case 2:
return time_field8409__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
time_field8409.cljs$core$IFn$_invoke$arity$1 = time_field8409__1;
time_field8409.cljs$core$IFn$_invoke$arity$2 = time_field8409__2;
return time_field8409;
})()
;
sablono.core.time_field = sablono.core.wrap_attrs(sablono.core.time_field8409);
/**
* Creates a url input field.
*/
sablono.core.url_field8410 = (function() {
var url_field8410 = null;
var url_field8410__1 = (function (name__5778__auto__){return url_field8410.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var url_field8410__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"url","url",-1640415448,null))),name__5778__auto__,value__5779__auto__);
});
url_field8410 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return url_field8410__1.call(this,name__5778__auto__);
case 2:
return url_field8410__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
url_field8410.cljs$core$IFn$_invoke$arity$1 = url_field8410__1;
url_field8410.cljs$core$IFn$_invoke$arity$2 = url_field8410__2;
return url_field8410;
})()
;
sablono.core.url_field = sablono.core.wrap_attrs(sablono.core.url_field8410);
/**
* Creates a week input field.
*/
sablono.core.week_field8411 = (function() {
var week_field8411 = null;
var week_field8411__1 = (function (name__5778__auto__){return week_field8411.cljs$core$IFn$_invoke$arity$2(name__5778__auto__,null);
});
var week_field8411__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"week","week",-1636886099,null))),name__5778__auto__,value__5779__auto__);
});
week_field8411 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return week_field8411__1.call(this,name__5778__auto__);
case 2:
return week_field8411__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
week_field8411.cljs$core$IFn$_invoke$arity$1 = week_field8411__1;
week_field8411.cljs$core$IFn$_invoke$arity$2 = week_field8411__2;
return week_field8411;
})()
;
sablono.core.week_field = sablono.core.wrap_attrs(sablono.core.week_field8411);
sablono.core.file_upload = sablono.core.file_field;
/**
* Creates a check box.
*/
sablono.core.check_box8412 = (function() {
var check_box8412 = null;
var check_box8412__1 = (function (name){return check_box8412.cljs$core$IFn$_invoke$arity$2(name,null);
});
var check_box8412__2 = (function (name,checked_QMARK_){return check_box8412.cljs$core$IFn$_invoke$arity$3(name,checked_QMARK_,"true");
});
var check_box8412__3 = (function (name,checked_QMARK_,value){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$36,new cljs.core.PersistentArrayMap(null, 5, [cljs.core.constant$keyword$38,"checkbox",cljs.core.constant$keyword$48,sablono.core.make_name(name),cljs.core.constant$keyword$34,sablono.core.make_id(name),cljs.core.constant$keyword$11,value,cljs.core.constant$keyword$49,checked_QMARK_], null)], null);
});
check_box8412 = function(name,checked_QMARK_,value){
switch(arguments.length){
case 1:
return check_box8412__1.call(this,name);
case 2:
return check_box8412__2.call(this,name,checked_QMARK_);
case 3:
return check_box8412__3.call(this,name,checked_QMARK_,value);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
check_box8412.cljs$core$IFn$_invoke$arity$1 = check_box8412__1;
check_box8412.cljs$core$IFn$_invoke$arity$2 = check_box8412__2;
check_box8412.cljs$core$IFn$_invoke$arity$3 = check_box8412__3;
return check_box8412;
})()
;
sablono.core.check_box = sablono.core.wrap_attrs(sablono.core.check_box8412);
/**
* Creates a radio button.
*/
sablono.core.radio_button8413 = (function() {
var radio_button8413 = null;
var radio_button8413__1 = (function (group){return radio_button8413.cljs$core$IFn$_invoke$arity$2(group,null);
});
var radio_button8413__2 = (function (group,checked_QMARK_){return radio_button8413.cljs$core$IFn$_invoke$arity$3(group,checked_QMARK_,"true");
});
var radio_button8413__3 = (function (group,checked_QMARK_,value){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$36,new cljs.core.PersistentArrayMap(null, 5, [cljs.core.constant$keyword$38,"radio",cljs.core.constant$keyword$48,sablono.core.make_name(group),cljs.core.constant$keyword$34,sablono.core.make_id((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(sablono.util.as_str.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([group], 0)))+"-"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(sablono.util.as_str.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([value], 0))))),cljs.core.constant$keyword$11,value,cljs.core.constant$keyword$49,checked_QMARK_], null)], null);
});
radio_button8413 = function(group,checked_QMARK_,value){
switch(arguments.length){
case 1:
return radio_button8413__1.call(this,group);
case 2:
return radio_button8413__2.call(this,group,checked_QMARK_);
case 3:
return radio_button8413__3.call(this,group,checked_QMARK_,value);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
radio_button8413.cljs$core$IFn$_invoke$arity$1 = radio_button8413__1;
radio_button8413.cljs$core$IFn$_invoke$arity$2 = radio_button8413__2;
radio_button8413.cljs$core$IFn$_invoke$arity$3 = radio_button8413__3;
return radio_button8413;
})()
;
sablono.core.radio_button = sablono.core.wrap_attrs(sablono.core.radio_button8413);
/**
* Creates a seq of option tags from a collection.
*/
sablono.core.select_options8414 = (function() {
var select_options8414 = null;
var select_options8414__1 = (function (coll){return select_options8414.cljs$core$IFn$_invoke$arity$2(coll,null);
});
var select_options8414__2 = (function (coll,selected){var iter__4298__auto__ = (function iter__8423(s__8424){return (new cljs.core.LazySeq(null,(function (){var s__8424__$1 = s__8424;while(true){
var temp__4126__auto__ = cljs.core.seq(s__8424__$1);if(temp__4126__auto__)
{var s__8424__$2 = temp__4126__auto__;if(cljs.core.chunked_seq_QMARK_(s__8424__$2))
{var c__4296__auto__ = cljs.core.chunk_first(s__8424__$2);var size__4297__auto__ = cljs.core.count(c__4296__auto__);var b__8426 = cljs.core.chunk_buffer(size__4297__auto__);if((function (){var i__8425 = 0;while(true){
if((i__8425 < size__4297__auto__))
{var x = cljs.core._nth.cljs$core$IFn$_invoke$arity$2(c__4296__auto__,i__8425);cljs.core.chunk_append(b__8426,((cljs.core.sequential_QMARK_(x))?(function (){var vec__8429 = x;var text = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8429,0,null);var val = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8429,1,null);var disabled_QMARK_ = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8429,2,null);var disabled_QMARK___$1 = cljs.core.boolean$(disabled_QMARK_);if(cljs.core.sequential_QMARK_(val))
{return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$50,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$51,text], null),select_options8414.cljs$core$IFn$_invoke$arity$2(val,selected)], null);
} else
{return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$52,new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$11,val,cljs.core.constant$keyword$53,cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2(val,selected),cljs.core.constant$keyword$54,disabled_QMARK___$1], null),text], null);
}
})():new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$52,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$53,cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2(x,selected)], null),x], null)));
{
var G__8431 = (i__8425 + 1);
i__8425 = G__8431;
continue;
}
} else
{return true;
}
break;
}
})())
{return cljs.core.chunk_cons(cljs.core.chunk(b__8426),iter__8423(cljs.core.chunk_rest(s__8424__$2)));
} else
{return cljs.core.chunk_cons(cljs.core.chunk(b__8426),null);
}
} else
{var x = cljs.core.first(s__8424__$2);return cljs.core.cons(((cljs.core.sequential_QMARK_(x))?(function (){var vec__8430 = x;var text = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8430,0,null);var val = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8430,1,null);var disabled_QMARK_ = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8430,2,null);var disabled_QMARK___$1 = cljs.core.boolean$(disabled_QMARK_);if(cljs.core.sequential_QMARK_(val))
{return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$50,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$51,text], null),select_options8414.cljs$core$IFn$_invoke$arity$2(val,selected)], null);
} else
{return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$52,new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$11,val,cljs.core.constant$keyword$53,cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2(val,selected),cljs.core.constant$keyword$54,disabled_QMARK___$1], null),text], null);
}
})():new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$52,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$53,cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2(x,selected)], null),x], null)),iter__8423(cljs.core.rest(s__8424__$2)));
}
} else
{return null;
}
break;
}
}),null,null));
});return iter__4298__auto__(coll);
});
select_options8414 = function(coll,selected){
switch(arguments.length){
case 1:
return select_options8414__1.call(this,coll);
case 2:
return select_options8414__2.call(this,coll,selected);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
select_options8414.cljs$core$IFn$_invoke$arity$1 = select_options8414__1;
select_options8414.cljs$core$IFn$_invoke$arity$2 = select_options8414__2;
return select_options8414;
})()
;
sablono.core.select_options = sablono.core.wrap_attrs(sablono.core.select_options8414);
/**
* Creates a drop-down box using the <select> tag.
*/
sablono.core.drop_down8432 = (function() {
var drop_down8432 = null;
var drop_down8432__2 = (function (name,options){return drop_down8432.cljs$core$IFn$_invoke$arity$3(name,options,null);
});
var drop_down8432__3 = (function (name,options,selected){return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$55,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$48,sablono.core.make_name(name),cljs.core.constant$keyword$34,sablono.core.make_id(name)], null),(sablono.core.select_options.cljs$core$IFn$_invoke$arity$2 ? sablono.core.select_options.cljs$core$IFn$_invoke$arity$2(options,selected) : sablono.core.select_options.call(null,options,selected))], null);
});
drop_down8432 = function(name,options,selected){
switch(arguments.length){
case 2:
return drop_down8432__2.call(this,name,options);
case 3:
return drop_down8432__3.call(this,name,options,selected);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
drop_down8432.cljs$core$IFn$_invoke$arity$2 = drop_down8432__2;
drop_down8432.cljs$core$IFn$_invoke$arity$3 = drop_down8432__3;
return drop_down8432;
})()
;
sablono.core.drop_down = sablono.core.wrap_attrs(sablono.core.drop_down8432);
/**
* Creates a text area element.
*/
sablono.core.text_area8433 = (function() {
var text_area8433 = null;
var text_area8433__1 = (function (name){return text_area8433.cljs$core$IFn$_invoke$arity$2(name,null);
});
var text_area8433__2 = (function (name,value){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$35,new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$48,sablono.core.make_name(name),cljs.core.constant$keyword$34,sablono.core.make_id(name),cljs.core.constant$keyword$11,value], null)], null);
});
text_area8433 = function(name,value){
switch(arguments.length){
case 1:
return text_area8433__1.call(this,name);
case 2:
return text_area8433__2.call(this,name,value);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
text_area8433.cljs$core$IFn$_invoke$arity$1 = text_area8433__1;
text_area8433.cljs$core$IFn$_invoke$arity$2 = text_area8433__2;
return text_area8433;
})()
;
sablono.core.text_area = sablono.core.wrap_attrs(sablono.core.text_area8433);
/**
* Creates a label for an input field with the supplied name.
*/
sablono.core.label8434 = (function label8434(name,text){return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$51,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$31,sablono.core.make_id(name)], null),text], null);
});
sablono.core.label = sablono.core.wrap_attrs(sablono.core.label8434);
/**
* Creates a submit button.
*/
sablono.core.submit_button8435 = (function submit_button8435(text){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$36,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$38,"submit",cljs.core.constant$keyword$11,text], null)], null);
});
sablono.core.submit_button = sablono.core.wrap_attrs(sablono.core.submit_button8435);
/**
* Creates a form reset button.
*/
sablono.core.reset_button8436 = (function reset_button8436(text){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$36,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$38,"reset",cljs.core.constant$keyword$11,text], null)], null);
});
sablono.core.reset_button = sablono.core.wrap_attrs(sablono.core.reset_button8436);
/**
* Create a form that points to a particular method and route.
* e.g. (form-to [:put "/post"]
* ...)
* @param {...*} var_args
*/
sablono.core.form_to8437 = (function() { 
var form_to8437__delegate = function (p__8438,body){var vec__8440 = p__8438;var method = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8440,0,null);var action = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__8440,1,null);var method_str = clojure.string.upper_case(cljs.core.name(method));var action_uri = sablono.util.to_uri(action);return cljs.core.vec(cljs.core.concat.cljs$core$IFn$_invoke$arity$2(((cljs.core.contains_QMARK_(new cljs.core.PersistentHashSet(null, new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$56,null,cljs.core.constant$keyword$57,null], null), null),method))?new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$58,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$59,method_str,cljs.core.constant$keyword$60,action_uri], null)], null):new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$58,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$59,"POST",cljs.core.constant$keyword$60,action_uri], null),(sablono.core.hidden_field.cljs$core$IFn$_invoke$arity$2 ? sablono.core.hidden_field.cljs$core$IFn$_invoke$arity$2("_method",method_str) : sablono.core.hidden_field.call(null,"_method",method_str))], null)),body));
};
var form_to8437 = function (p__8438,var_args){
var body = null;if (arguments.length > 1) {
  body = cljs.core.array_seq(Array.prototype.slice.call(arguments, 1),0);} 
return form_to8437__delegate.call(this,p__8438,body);};
form_to8437.cljs$lang$maxFixedArity = 1;
form_to8437.cljs$lang$applyTo = (function (arglist__8441){
var p__8438 = cljs.core.first(arglist__8441);
var body = cljs.core.rest(arglist__8441);
return form_to8437__delegate(p__8438,body);
});
form_to8437.cljs$core$IFn$_invoke$arity$variadic = form_to8437__delegate;
return form_to8437;
})()
;
sablono.core.form_to = sablono.core.wrap_attrs(sablono.core.form_to8437);
