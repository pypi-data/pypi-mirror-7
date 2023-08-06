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
var G__8327__delegate = function (args){if(cljs.core.map_QMARK_.call(null,cljs.core.first.call(null,args)))
{var vec__8326 = cljs.core.apply.call(null,func,cljs.core.rest.call(null,args));var tag = cljs.core.nth.call(null,vec__8326,0,null);var body = cljs.core.nthnext.call(null,vec__8326,1);if(cljs.core.map_QMARK_.call(null,cljs.core.first.call(null,body)))
{return cljs.core.apply.call(null,cljs.core.vector,tag,cljs.core.merge.call(null,cljs.core.first.call(null,body),cljs.core.first.call(null,args)),cljs.core.rest.call(null,body));
} else
{return cljs.core.apply.call(null,cljs.core.vector,tag,cljs.core.first.call(null,args),body);
}
} else
{return cljs.core.apply.call(null,func,args);
}
};
var G__8327 = function (var_args){
var args = null;if (arguments.length > 0) {
  args = cljs.core.array_seq(Array.prototype.slice.call(arguments, 0),0);} 
return G__8327__delegate.call(this,args);};
G__8327.cljs$lang$maxFixedArity = 0;
G__8327.cljs$lang$applyTo = (function (arglist__8328){
var args = cljs.core.seq(arglist__8328);
return G__8327__delegate(args);
});
G__8327.cljs$core$IFn$_invoke$arity$variadic = G__8327__delegate;
return G__8327;
})()
;
});
sablono.core.update_arglists = (function update_arglists(arglists){var iter__4298__auto__ = (function iter__8333(s__8334){return (new cljs.core.LazySeq(null,(function (){var s__8334__$1 = s__8334;while(true){
var temp__4126__auto__ = cljs.core.seq.call(null,s__8334__$1);if(temp__4126__auto__)
{var s__8334__$2 = temp__4126__auto__;if(cljs.core.chunked_seq_QMARK_.call(null,s__8334__$2))
{var c__4296__auto__ = cljs.core.chunk_first.call(null,s__8334__$2);var size__4297__auto__ = cljs.core.count.call(null,c__4296__auto__);var b__8336 = cljs.core.chunk_buffer.call(null,size__4297__auto__);if((function (){var i__8335 = 0;while(true){
if((i__8335 < size__4297__auto__))
{var args = cljs.core._nth.call(null,c__4296__auto__,i__8335);cljs.core.chunk_append.call(null,b__8336,cljs.core.vec.call(null,cljs.core.cons.call(null,new cljs.core.Symbol(null,"attr-map?","attr-map?",-1682549128,null),args)));
{
var G__8337 = (i__8335 + 1);
i__8335 = G__8337;
continue;
}
} else
{return true;
}
break;
}
})())
{return cljs.core.chunk_cons.call(null,cljs.core.chunk.call(null,b__8336),iter__8333.call(null,cljs.core.chunk_rest.call(null,s__8334__$2)));
} else
{return cljs.core.chunk_cons.call(null,cljs.core.chunk.call(null,b__8336),null);
}
} else
{var args = cljs.core.first.call(null,s__8334__$2);return cljs.core.cons.call(null,cljs.core.vec.call(null,cljs.core.cons.call(null,new cljs.core.Symbol(null,"attr-map?","attr-map?",-1682549128,null),args)),iter__8333.call(null,cljs.core.rest.call(null,s__8334__$2)));
}
} else
{return null;
}
break;
}
}),null,null));
});return iter__4298__auto__.call(null,arglists);
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
var include_css__delegate = function (styles){var iter__4298__auto__ = (function iter__8342(s__8343){return (new cljs.core.LazySeq(null,(function (){var s__8343__$1 = s__8343;while(true){
var temp__4126__auto__ = cljs.core.seq.call(null,s__8343__$1);if(temp__4126__auto__)
{var s__8343__$2 = temp__4126__auto__;if(cljs.core.chunked_seq_QMARK_.call(null,s__8343__$2))
{var c__4296__auto__ = cljs.core.chunk_first.call(null,s__8343__$2);var size__4297__auto__ = cljs.core.count.call(null,c__4296__auto__);var b__8345 = cljs.core.chunk_buffer.call(null,size__4297__auto__);if((function (){var i__8344 = 0;while(true){
if((i__8344 < size__4297__auto__))
{var style = cljs.core._nth.call(null,c__4296__auto__,i__8344);cljs.core.chunk_append.call(null,b__8345,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"link","link",1017226092),new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"type","type",1017479852),"text/css",new cljs.core.Keyword(null,"href","href",1017115293),sablono.util.as_str.call(null,style),new cljs.core.Keyword(null,"rel","rel",1014017035),"stylesheet"], null)], null));
{
var G__8346 = (i__8344 + 1);
i__8344 = G__8346;
continue;
}
} else
{return true;
}
break;
}
})())
{return cljs.core.chunk_cons.call(null,cljs.core.chunk.call(null,b__8345),iter__8342.call(null,cljs.core.chunk_rest.call(null,s__8343__$2)));
} else
{return cljs.core.chunk_cons.call(null,cljs.core.chunk.call(null,b__8345),null);
}
} else
{var style = cljs.core.first.call(null,s__8343__$2);return cljs.core.cons.call(null,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"link","link",1017226092),new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"type","type",1017479852),"text/css",new cljs.core.Keyword(null,"href","href",1017115293),sablono.util.as_str.call(null,style),new cljs.core.Keyword(null,"rel","rel",1014017035),"stylesheet"], null)], null),iter__8342.call(null,cljs.core.rest.call(null,s__8343__$2)));
}
} else
{return null;
}
break;
}
}),null,null));
});return iter__4298__auto__.call(null,styles);
};
var include_css = function (var_args){
var styles = null;if (arguments.length > 0) {
  styles = cljs.core.array_seq(Array.prototype.slice.call(arguments, 0),0);} 
return include_css__delegate.call(this,styles);};
include_css.cljs$lang$maxFixedArity = 0;
include_css.cljs$lang$applyTo = (function (arglist__8347){
var styles = cljs.core.seq(arglist__8347);
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
sablono.core.include_react = (function include_react(){return sablono.core.include_js.call(null,"http://fb.me/react-0.9.0.js");
});
/**
* Wraps some content in a HTML hyperlink with the supplied URL.
* @param {...*} var_args
*/
sablono.core.link_to8348 = (function() { 
var link_to8348__delegate = function (url,content){return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"a","a",1013904339),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"href","href",1017115293),sablono.util.as_str.call(null,url)], null),content], null);
};
var link_to8348 = function (url,var_args){
var content = null;if (arguments.length > 1) {
  content = cljs.core.array_seq(Array.prototype.slice.call(arguments, 1),0);} 
return link_to8348__delegate.call(this,url,content);};
link_to8348.cljs$lang$maxFixedArity = 1;
link_to8348.cljs$lang$applyTo = (function (arglist__8349){
var url = cljs.core.first(arglist__8349);
var content = cljs.core.rest(arglist__8349);
return link_to8348__delegate(url,content);
});
link_to8348.cljs$core$IFn$_invoke$arity$variadic = link_to8348__delegate;
return link_to8348;
})()
;
sablono.core.link_to = sablono.core.wrap_attrs.call(null,sablono.core.link_to8348);
/**
* Wraps some content in a HTML hyperlink with the supplied e-mail
* address. If no content provided use the e-mail address as content.
* @param {...*} var_args
*/
sablono.core.mail_to8350 = (function() { 
var mail_to8350__delegate = function (e_mail,p__8351){var vec__8353 = p__8351;var content = cljs.core.nth.call(null,vec__8353,0,null);return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"a","a",1013904339),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"href","href",1017115293),("mailto:"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(e_mail))], null),(function (){var or__3573__auto__ = content;if(cljs.core.truth_(or__3573__auto__))
{return or__3573__auto__;
} else
{return e_mail;
}
})()], null);
};
var mail_to8350 = function (e_mail,var_args){
var p__8351 = null;if (arguments.length > 1) {
  p__8351 = cljs.core.array_seq(Array.prototype.slice.call(arguments, 1),0);} 
return mail_to8350__delegate.call(this,e_mail,p__8351);};
mail_to8350.cljs$lang$maxFixedArity = 1;
mail_to8350.cljs$lang$applyTo = (function (arglist__8354){
var e_mail = cljs.core.first(arglist__8354);
var p__8351 = cljs.core.rest(arglist__8354);
return mail_to8350__delegate(e_mail,p__8351);
});
mail_to8350.cljs$core$IFn$_invoke$arity$variadic = mail_to8350__delegate;
return mail_to8350;
})()
;
sablono.core.mail_to = sablono.core.wrap_attrs.call(null,sablono.core.mail_to8350);
/**
* Wrap a collection in an unordered list.
*/
sablono.core.unordered_list8355 = (function unordered_list8355(coll){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"ul","ul",1013907977),(function (){var iter__4298__auto__ = (function iter__8360(s__8361){return (new cljs.core.LazySeq(null,(function (){var s__8361__$1 = s__8361;while(true){
var temp__4126__auto__ = cljs.core.seq.call(null,s__8361__$1);if(temp__4126__auto__)
{var s__8361__$2 = temp__4126__auto__;if(cljs.core.chunked_seq_QMARK_.call(null,s__8361__$2))
{var c__4296__auto__ = cljs.core.chunk_first.call(null,s__8361__$2);var size__4297__auto__ = cljs.core.count.call(null,c__4296__auto__);var b__8363 = cljs.core.chunk_buffer.call(null,size__4297__auto__);if((function (){var i__8362 = 0;while(true){
if((i__8362 < size__4297__auto__))
{var x = cljs.core._nth.call(null,c__4296__auto__,i__8362);cljs.core.chunk_append.call(null,b__8363,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"li","li",1013907695),x], null));
{
var G__8364 = (i__8362 + 1);
i__8362 = G__8364;
continue;
}
} else
{return true;
}
break;
}
})())
{return cljs.core.chunk_cons.call(null,cljs.core.chunk.call(null,b__8363),iter__8360.call(null,cljs.core.chunk_rest.call(null,s__8361__$2)));
} else
{return cljs.core.chunk_cons.call(null,cljs.core.chunk.call(null,b__8363),null);
}
} else
{var x = cljs.core.first.call(null,s__8361__$2);return cljs.core.cons.call(null,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"li","li",1013907695),x], null),iter__8360.call(null,cljs.core.rest.call(null,s__8361__$2)));
}
} else
{return null;
}
break;
}
}),null,null));
});return iter__4298__auto__.call(null,coll);
})()], null);
});
sablono.core.unordered_list = sablono.core.wrap_attrs.call(null,sablono.core.unordered_list8355);
/**
* Wrap a collection in an ordered list.
*/
sablono.core.ordered_list8365 = (function ordered_list8365(coll){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"ol","ol",1013907791),(function (){var iter__4298__auto__ = (function iter__8370(s__8371){return (new cljs.core.LazySeq(null,(function (){var s__8371__$1 = s__8371;while(true){
var temp__4126__auto__ = cljs.core.seq.call(null,s__8371__$1);if(temp__4126__auto__)
{var s__8371__$2 = temp__4126__auto__;if(cljs.core.chunked_seq_QMARK_.call(null,s__8371__$2))
{var c__4296__auto__ = cljs.core.chunk_first.call(null,s__8371__$2);var size__4297__auto__ = cljs.core.count.call(null,c__4296__auto__);var b__8373 = cljs.core.chunk_buffer.call(null,size__4297__auto__);if((function (){var i__8372 = 0;while(true){
if((i__8372 < size__4297__auto__))
{var x = cljs.core._nth.call(null,c__4296__auto__,i__8372);cljs.core.chunk_append.call(null,b__8373,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"li","li",1013907695),x], null));
{
var G__8374 = (i__8372 + 1);
i__8372 = G__8374;
continue;
}
} else
{return true;
}
break;
}
})())
{return cljs.core.chunk_cons.call(null,cljs.core.chunk.call(null,b__8373),iter__8370.call(null,cljs.core.chunk_rest.call(null,s__8371__$2)));
} else
{return cljs.core.chunk_cons.call(null,cljs.core.chunk.call(null,b__8373),null);
}
} else
{var x = cljs.core.first.call(null,s__8371__$2);return cljs.core.cons.call(null,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"li","li",1013907695),x], null),iter__8370.call(null,cljs.core.rest.call(null,s__8371__$2)));
}
} else
{return null;
}
break;
}
}),null,null));
});return iter__4298__auto__.call(null,coll);
})()], null);
});
sablono.core.ordered_list = sablono.core.wrap_attrs.call(null,sablono.core.ordered_list8365);
/**
* Create an image element.
*/
sablono.core.image8375 = (function() {
var image8375 = null;
var image8375__1 = (function (src){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"img","img",1014008629),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"src","src",1014018390),sablono.util.as_str.call(null,src)], null)], null);
});
var image8375__2 = (function (src,alt){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"img","img",1014008629),new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"src","src",1014018390),sablono.util.as_str.call(null,src),new cljs.core.Keyword(null,"alt","alt",1014000923),alt], null)], null);
});
image8375 = function(src,alt){
switch(arguments.length){
case 1:
return image8375__1.call(this,src);
case 2:
return image8375__2.call(this,src,alt);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
image8375.cljs$core$IFn$_invoke$arity$1 = image8375__1;
image8375.cljs$core$IFn$_invoke$arity$2 = image8375__2;
return image8375;
})()
;
sablono.core.image = sablono.core.wrap_attrs.call(null,sablono.core.image8375);
sablono.core._STAR_group_STAR_ = cljs.core.PersistentVector.EMPTY;
/**
* Create a field name from the supplied argument the current field group.
*/
sablono.core.make_name = (function make_name(name){return cljs.core.reduce.call(null,(function (p1__8376_SHARP_,p2__8377_SHARP_){return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(p1__8376_SHARP_)+"["+cljs.core.str.cljs$core$IFn$_invoke$arity$1(p2__8377_SHARP_)+"]");
}),cljs.core.conj.call(null,sablono.core._STAR_group_STAR_,sablono.util.as_str.call(null,name)));
});
/**
* Create a field id from the supplied argument and current field group.
*/
sablono.core.make_id = (function make_id(name){return cljs.core.reduce.call(null,(function (p1__8378_SHARP_,p2__8379_SHARP_){return (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(p1__8378_SHARP_)+"-"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(p2__8379_SHARP_));
}),cljs.core.conj.call(null,sablono.core._STAR_group_STAR_,sablono.util.as_str.call(null,name)));
});
/**
* Creates a new <input> element.
*/
sablono.core.input_field_STAR_ = (function input_field_STAR_(type,name,value){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"input","input",1114262332),new cljs.core.PersistentArrayMap(null, 4, [new cljs.core.Keyword(null,"type","type",1017479852),type,new cljs.core.Keyword(null,"name","name",1017277949),sablono.core.make_name.call(null,name),new cljs.core.Keyword(null,"id","id",1013907597),sablono.core.make_id.call(null,name),new cljs.core.Keyword(null,"value","value",1125876963),value], null)], null);
});
/**
* Creates a color input field.
*/
sablono.core.color_field8380 = (function() {
var color_field8380 = null;
var color_field8380__1 = (function (name__5778__auto__){return color_field8380.call(null,name__5778__auto__,null);
});
var color_field8380__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"color","color",-1545688804,null))),name__5778__auto__,value__5779__auto__);
});
color_field8380 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return color_field8380__1.call(this,name__5778__auto__);
case 2:
return color_field8380__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
color_field8380.cljs$core$IFn$_invoke$arity$1 = color_field8380__1;
color_field8380.cljs$core$IFn$_invoke$arity$2 = color_field8380__2;
return color_field8380;
})()
;
sablono.core.color_field = sablono.core.wrap_attrs.call(null,sablono.core.color_field8380);
/**
* Creates a date input field.
*/
sablono.core.date_field8381 = (function() {
var date_field8381 = null;
var date_field8381__1 = (function (name__5778__auto__){return date_field8381.call(null,name__5778__auto__,null);
});
var date_field8381__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"date","date",-1637455513,null))),name__5778__auto__,value__5779__auto__);
});
date_field8381 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return date_field8381__1.call(this,name__5778__auto__);
case 2:
return date_field8381__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
date_field8381.cljs$core$IFn$_invoke$arity$1 = date_field8381__1;
date_field8381.cljs$core$IFn$_invoke$arity$2 = date_field8381__2;
return date_field8381;
})()
;
sablono.core.date_field = sablono.core.wrap_attrs.call(null,sablono.core.date_field8381);
/**
* Creates a datetime input field.
*/
sablono.core.datetime_field8382 = (function() {
var datetime_field8382 = null;
var datetime_field8382__1 = (function (name__5778__auto__){return datetime_field8382.call(null,name__5778__auto__,null);
});
var datetime_field8382__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"datetime","datetime",153171252,null))),name__5778__auto__,value__5779__auto__);
});
datetime_field8382 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return datetime_field8382__1.call(this,name__5778__auto__);
case 2:
return datetime_field8382__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
datetime_field8382.cljs$core$IFn$_invoke$arity$1 = datetime_field8382__1;
datetime_field8382.cljs$core$IFn$_invoke$arity$2 = datetime_field8382__2;
return datetime_field8382;
})()
;
sablono.core.datetime_field = sablono.core.wrap_attrs.call(null,sablono.core.datetime_field8382);
/**
* Creates a datetime-local input field.
*/
sablono.core.datetime_local_field8383 = (function() {
var datetime_local_field8383 = null;
var datetime_local_field8383__1 = (function (name__5778__auto__){return datetime_local_field8383.call(null,name__5778__auto__,null);
});
var datetime_local_field8383__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"datetime-local","datetime-local",1631019090,null))),name__5778__auto__,value__5779__auto__);
});
datetime_local_field8383 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return datetime_local_field8383__1.call(this,name__5778__auto__);
case 2:
return datetime_local_field8383__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
datetime_local_field8383.cljs$core$IFn$_invoke$arity$1 = datetime_local_field8383__1;
datetime_local_field8383.cljs$core$IFn$_invoke$arity$2 = datetime_local_field8383__2;
return datetime_local_field8383;
})()
;
sablono.core.datetime_local_field = sablono.core.wrap_attrs.call(null,sablono.core.datetime_local_field8383);
/**
* Creates a email input field.
*/
sablono.core.email_field8384 = (function() {
var email_field8384 = null;
var email_field8384__1 = (function (name__5778__auto__){return email_field8384.call(null,name__5778__auto__,null);
});
var email_field8384__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"email","email",-1543912107,null))),name__5778__auto__,value__5779__auto__);
});
email_field8384 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return email_field8384__1.call(this,name__5778__auto__);
case 2:
return email_field8384__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
email_field8384.cljs$core$IFn$_invoke$arity$1 = email_field8384__1;
email_field8384.cljs$core$IFn$_invoke$arity$2 = email_field8384__2;
return email_field8384;
})()
;
sablono.core.email_field = sablono.core.wrap_attrs.call(null,sablono.core.email_field8384);
/**
* Creates a file input field.
*/
sablono.core.file_field8385 = (function() {
var file_field8385 = null;
var file_field8385__1 = (function (name__5778__auto__){return file_field8385.call(null,name__5778__auto__,null);
});
var file_field8385__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"file","file",-1637388491,null))),name__5778__auto__,value__5779__auto__);
});
file_field8385 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return file_field8385__1.call(this,name__5778__auto__);
case 2:
return file_field8385__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
file_field8385.cljs$core$IFn$_invoke$arity$1 = file_field8385__1;
file_field8385.cljs$core$IFn$_invoke$arity$2 = file_field8385__2;
return file_field8385;
})()
;
sablono.core.file_field = sablono.core.wrap_attrs.call(null,sablono.core.file_field8385);
/**
* Creates a hidden input field.
*/
sablono.core.hidden_field8386 = (function() {
var hidden_field8386 = null;
var hidden_field8386__1 = (function (name__5778__auto__){return hidden_field8386.call(null,name__5778__auto__,null);
});
var hidden_field8386__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"hidden","hidden",1436948323,null))),name__5778__auto__,value__5779__auto__);
});
hidden_field8386 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return hidden_field8386__1.call(this,name__5778__auto__);
case 2:
return hidden_field8386__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
hidden_field8386.cljs$core$IFn$_invoke$arity$1 = hidden_field8386__1;
hidden_field8386.cljs$core$IFn$_invoke$arity$2 = hidden_field8386__2;
return hidden_field8386;
})()
;
sablono.core.hidden_field = sablono.core.wrap_attrs.call(null,sablono.core.hidden_field8386);
/**
* Creates a month input field.
*/
sablono.core.month_field8387 = (function() {
var month_field8387 = null;
var month_field8387__1 = (function (name__5778__auto__){return month_field8387.call(null,name__5778__auto__,null);
});
var month_field8387__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"month","month",-1536451527,null))),name__5778__auto__,value__5779__auto__);
});
month_field8387 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return month_field8387__1.call(this,name__5778__auto__);
case 2:
return month_field8387__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
month_field8387.cljs$core$IFn$_invoke$arity$1 = month_field8387__1;
month_field8387.cljs$core$IFn$_invoke$arity$2 = month_field8387__2;
return month_field8387;
})()
;
sablono.core.month_field = sablono.core.wrap_attrs.call(null,sablono.core.month_field8387);
/**
* Creates a number input field.
*/
sablono.core.number_field8388 = (function() {
var number_field8388 = null;
var number_field8388__1 = (function (name__5778__auto__){return number_field8388.call(null,name__5778__auto__,null);
});
var number_field8388__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"number","number",1620071682,null))),name__5778__auto__,value__5779__auto__);
});
number_field8388 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return number_field8388__1.call(this,name__5778__auto__);
case 2:
return number_field8388__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
number_field8388.cljs$core$IFn$_invoke$arity$1 = number_field8388__1;
number_field8388.cljs$core$IFn$_invoke$arity$2 = number_field8388__2;
return number_field8388;
})()
;
sablono.core.number_field = sablono.core.wrap_attrs.call(null,sablono.core.number_field8388);
/**
* Creates a password input field.
*/
sablono.core.password_field8389 = (function() {
var password_field8389 = null;
var password_field8389__1 = (function (name__5778__auto__){return password_field8389.call(null,name__5778__auto__,null);
});
var password_field8389__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"password","password",-423545772,null))),name__5778__auto__,value__5779__auto__);
});
password_field8389 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return password_field8389__1.call(this,name__5778__auto__);
case 2:
return password_field8389__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
password_field8389.cljs$core$IFn$_invoke$arity$1 = password_field8389__1;
password_field8389.cljs$core$IFn$_invoke$arity$2 = password_field8389__2;
return password_field8389;
})()
;
sablono.core.password_field = sablono.core.wrap_attrs.call(null,sablono.core.password_field8389);
/**
* Creates a range input field.
*/
sablono.core.range_field8390 = (function() {
var range_field8390 = null;
var range_field8390__1 = (function (name__5778__auto__){return range_field8390.call(null,name__5778__auto__,null);
});
var range_field8390__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"range","range",-1532251402,null))),name__5778__auto__,value__5779__auto__);
});
range_field8390 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return range_field8390__1.call(this,name__5778__auto__);
case 2:
return range_field8390__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
range_field8390.cljs$core$IFn$_invoke$arity$1 = range_field8390__1;
range_field8390.cljs$core$IFn$_invoke$arity$2 = range_field8390__2;
return range_field8390;
})()
;
sablono.core.range_field = sablono.core.wrap_attrs.call(null,sablono.core.range_field8390);
/**
* Creates a search input field.
*/
sablono.core.search_field8391 = (function() {
var search_field8391 = null;
var search_field8391__1 = (function (name__5778__auto__){return search_field8391.call(null,name__5778__auto__,null);
});
var search_field8391__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"search","search",1748098913,null))),name__5778__auto__,value__5779__auto__);
});
search_field8391 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return search_field8391__1.call(this,name__5778__auto__);
case 2:
return search_field8391__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
search_field8391.cljs$core$IFn$_invoke$arity$1 = search_field8391__1;
search_field8391.cljs$core$IFn$_invoke$arity$2 = search_field8391__2;
return search_field8391;
})()
;
sablono.core.search_field = sablono.core.wrap_attrs.call(null,sablono.core.search_field8391);
/**
* Creates a tel input field.
*/
sablono.core.tel_field8392 = (function() {
var tel_field8392 = null;
var tel_field8392__1 = (function (name__5778__auto__){return tel_field8392.call(null,name__5778__auto__,null);
});
var tel_field8392__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"tel","tel",-1640416812,null))),name__5778__auto__,value__5779__auto__);
});
tel_field8392 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return tel_field8392__1.call(this,name__5778__auto__);
case 2:
return tel_field8392__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
tel_field8392.cljs$core$IFn$_invoke$arity$1 = tel_field8392__1;
tel_field8392.cljs$core$IFn$_invoke$arity$2 = tel_field8392__2;
return tel_field8392;
})()
;
sablono.core.tel_field = sablono.core.wrap_attrs.call(null,sablono.core.tel_field8392);
/**
* Creates a text input field.
*/
sablono.core.text_field8393 = (function() {
var text_field8393 = null;
var text_field8393__1 = (function (name__5778__auto__){return text_field8393.call(null,name__5778__auto__,null);
});
var text_field8393__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"text","text",-1636974874,null))),name__5778__auto__,value__5779__auto__);
});
text_field8393 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return text_field8393__1.call(this,name__5778__auto__);
case 2:
return text_field8393__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
text_field8393.cljs$core$IFn$_invoke$arity$1 = text_field8393__1;
text_field8393.cljs$core$IFn$_invoke$arity$2 = text_field8393__2;
return text_field8393;
})()
;
sablono.core.text_field = sablono.core.wrap_attrs.call(null,sablono.core.text_field8393);
/**
* Creates a time input field.
*/
sablono.core.time_field8394 = (function() {
var time_field8394 = null;
var time_field8394__1 = (function (name__5778__auto__){return time_field8394.call(null,name__5778__auto__,null);
});
var time_field8394__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"time","time",-1636971386,null))),name__5778__auto__,value__5779__auto__);
});
time_field8394 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return time_field8394__1.call(this,name__5778__auto__);
case 2:
return time_field8394__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
time_field8394.cljs$core$IFn$_invoke$arity$1 = time_field8394__1;
time_field8394.cljs$core$IFn$_invoke$arity$2 = time_field8394__2;
return time_field8394;
})()
;
sablono.core.time_field = sablono.core.wrap_attrs.call(null,sablono.core.time_field8394);
/**
* Creates a url input field.
*/
sablono.core.url_field8395 = (function() {
var url_field8395 = null;
var url_field8395__1 = (function (name__5778__auto__){return url_field8395.call(null,name__5778__auto__,null);
});
var url_field8395__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"url","url",-1640415448,null))),name__5778__auto__,value__5779__auto__);
});
url_field8395 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return url_field8395__1.call(this,name__5778__auto__);
case 2:
return url_field8395__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
url_field8395.cljs$core$IFn$_invoke$arity$1 = url_field8395__1;
url_field8395.cljs$core$IFn$_invoke$arity$2 = url_field8395__2;
return url_field8395;
})()
;
sablono.core.url_field = sablono.core.wrap_attrs.call(null,sablono.core.url_field8395);
/**
* Creates a week input field.
*/
sablono.core.week_field8396 = (function() {
var week_field8396 = null;
var week_field8396__1 = (function (name__5778__auto__){return week_field8396.call(null,name__5778__auto__,null);
});
var week_field8396__2 = (function (name__5778__auto__,value__5779__auto__){return sablono.core.input_field_STAR_.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(new cljs.core.Symbol(null,"week","week",-1636886099,null))),name__5778__auto__,value__5779__auto__);
});
week_field8396 = function(name__5778__auto__,value__5779__auto__){
switch(arguments.length){
case 1:
return week_field8396__1.call(this,name__5778__auto__);
case 2:
return week_field8396__2.call(this,name__5778__auto__,value__5779__auto__);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
week_field8396.cljs$core$IFn$_invoke$arity$1 = week_field8396__1;
week_field8396.cljs$core$IFn$_invoke$arity$2 = week_field8396__2;
return week_field8396;
})()
;
sablono.core.week_field = sablono.core.wrap_attrs.call(null,sablono.core.week_field8396);
sablono.core.file_upload = sablono.core.file_field;
/**
* Creates a check box.
*/
sablono.core.check_box8397 = (function() {
var check_box8397 = null;
var check_box8397__1 = (function (name){return check_box8397.call(null,name,null);
});
var check_box8397__2 = (function (name,checked_QMARK_){return check_box8397.call(null,name,checked_QMARK_,"true");
});
var check_box8397__3 = (function (name,checked_QMARK_,value){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"input","input",1114262332),new cljs.core.PersistentArrayMap(null, 5, [new cljs.core.Keyword(null,"type","type",1017479852),"checkbox",new cljs.core.Keyword(null,"name","name",1017277949),sablono.core.make_name.call(null,name),new cljs.core.Keyword(null,"id","id",1013907597),sablono.core.make_id.call(null,name),new cljs.core.Keyword(null,"value","value",1125876963),value,new cljs.core.Keyword(null,"checked","checked",1756218137),checked_QMARK_], null)], null);
});
check_box8397 = function(name,checked_QMARK_,value){
switch(arguments.length){
case 1:
return check_box8397__1.call(this,name);
case 2:
return check_box8397__2.call(this,name,checked_QMARK_);
case 3:
return check_box8397__3.call(this,name,checked_QMARK_,value);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
check_box8397.cljs$core$IFn$_invoke$arity$1 = check_box8397__1;
check_box8397.cljs$core$IFn$_invoke$arity$2 = check_box8397__2;
check_box8397.cljs$core$IFn$_invoke$arity$3 = check_box8397__3;
return check_box8397;
})()
;
sablono.core.check_box = sablono.core.wrap_attrs.call(null,sablono.core.check_box8397);
/**
* Creates a radio button.
*/
sablono.core.radio_button8398 = (function() {
var radio_button8398 = null;
var radio_button8398__1 = (function (group){return radio_button8398.call(null,group,null);
});
var radio_button8398__2 = (function (group,checked_QMARK_){return radio_button8398.call(null,group,checked_QMARK_,"true");
});
var radio_button8398__3 = (function (group,checked_QMARK_,value){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"input","input",1114262332),new cljs.core.PersistentArrayMap(null, 5, [new cljs.core.Keyword(null,"type","type",1017479852),"radio",new cljs.core.Keyword(null,"name","name",1017277949),sablono.core.make_name.call(null,group),new cljs.core.Keyword(null,"id","id",1013907597),sablono.core.make_id.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(sablono.util.as_str.call(null,group))+"-"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(sablono.util.as_str.call(null,value)))),new cljs.core.Keyword(null,"value","value",1125876963),value,new cljs.core.Keyword(null,"checked","checked",1756218137),checked_QMARK_], null)], null);
});
radio_button8398 = function(group,checked_QMARK_,value){
switch(arguments.length){
case 1:
return radio_button8398__1.call(this,group);
case 2:
return radio_button8398__2.call(this,group,checked_QMARK_);
case 3:
return radio_button8398__3.call(this,group,checked_QMARK_,value);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
radio_button8398.cljs$core$IFn$_invoke$arity$1 = radio_button8398__1;
radio_button8398.cljs$core$IFn$_invoke$arity$2 = radio_button8398__2;
radio_button8398.cljs$core$IFn$_invoke$arity$3 = radio_button8398__3;
return radio_button8398;
})()
;
sablono.core.radio_button = sablono.core.wrap_attrs.call(null,sablono.core.radio_button8398);
/**
* Creates a seq of option tags from a collection.
*/
sablono.core.select_options8399 = (function() {
var select_options8399 = null;
var select_options8399__1 = (function (coll){return select_options8399.call(null,coll,null);
});
var select_options8399__2 = (function (coll,selected){var iter__4298__auto__ = (function iter__8408(s__8409){return (new cljs.core.LazySeq(null,(function (){var s__8409__$1 = s__8409;while(true){
var temp__4126__auto__ = cljs.core.seq.call(null,s__8409__$1);if(temp__4126__auto__)
{var s__8409__$2 = temp__4126__auto__;if(cljs.core.chunked_seq_QMARK_.call(null,s__8409__$2))
{var c__4296__auto__ = cljs.core.chunk_first.call(null,s__8409__$2);var size__4297__auto__ = cljs.core.count.call(null,c__4296__auto__);var b__8411 = cljs.core.chunk_buffer.call(null,size__4297__auto__);if((function (){var i__8410 = 0;while(true){
if((i__8410 < size__4297__auto__))
{var x = cljs.core._nth.call(null,c__4296__auto__,i__8410);cljs.core.chunk_append.call(null,b__8411,((cljs.core.sequential_QMARK_.call(null,x))?(function (){var vec__8414 = x;var text = cljs.core.nth.call(null,vec__8414,0,null);var val = cljs.core.nth.call(null,vec__8414,1,null);var disabled_QMARK_ = cljs.core.nth.call(null,vec__8414,2,null);var disabled_QMARK___$1 = cljs.core.boolean$.call(null,disabled_QMARK_);if(cljs.core.sequential_QMARK_.call(null,val))
{return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"optgroup","optgroup",933131038),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"label","label",1116631654),text], null),select_options8399.call(null,val,selected)], null);
} else
{return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"option","option",4298734567),new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"value","value",1125876963),val,new cljs.core.Keyword(null,"selected","selected",2205476365),cljs.core._EQ_.call(null,val,selected),new cljs.core.Keyword(null,"disabled","disabled",1284845038),disabled_QMARK___$1], null),text], null);
}
})():new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"option","option",4298734567),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"selected","selected",2205476365),cljs.core._EQ_.call(null,x,selected)], null),x], null)));
{
var G__8416 = (i__8410 + 1);
i__8410 = G__8416;
continue;
}
} else
{return true;
}
break;
}
})())
{return cljs.core.chunk_cons.call(null,cljs.core.chunk.call(null,b__8411),iter__8408.call(null,cljs.core.chunk_rest.call(null,s__8409__$2)));
} else
{return cljs.core.chunk_cons.call(null,cljs.core.chunk.call(null,b__8411),null);
}
} else
{var x = cljs.core.first.call(null,s__8409__$2);return cljs.core.cons.call(null,((cljs.core.sequential_QMARK_.call(null,x))?(function (){var vec__8415 = x;var text = cljs.core.nth.call(null,vec__8415,0,null);var val = cljs.core.nth.call(null,vec__8415,1,null);var disabled_QMARK_ = cljs.core.nth.call(null,vec__8415,2,null);var disabled_QMARK___$1 = cljs.core.boolean$.call(null,disabled_QMARK_);if(cljs.core.sequential_QMARK_.call(null,val))
{return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"optgroup","optgroup",933131038),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"label","label",1116631654),text], null),select_options8399.call(null,val,selected)], null);
} else
{return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"option","option",4298734567),new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"value","value",1125876963),val,new cljs.core.Keyword(null,"selected","selected",2205476365),cljs.core._EQ_.call(null,val,selected),new cljs.core.Keyword(null,"disabled","disabled",1284845038),disabled_QMARK___$1], null),text], null);
}
})():new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"option","option",4298734567),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"selected","selected",2205476365),cljs.core._EQ_.call(null,x,selected)], null),x], null)),iter__8408.call(null,cljs.core.rest.call(null,s__8409__$2)));
}
} else
{return null;
}
break;
}
}),null,null));
});return iter__4298__auto__.call(null,coll);
});
select_options8399 = function(coll,selected){
switch(arguments.length){
case 1:
return select_options8399__1.call(this,coll);
case 2:
return select_options8399__2.call(this,coll,selected);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
select_options8399.cljs$core$IFn$_invoke$arity$1 = select_options8399__1;
select_options8399.cljs$core$IFn$_invoke$arity$2 = select_options8399__2;
return select_options8399;
})()
;
sablono.core.select_options = sablono.core.wrap_attrs.call(null,sablono.core.select_options8399);
/**
* Creates a drop-down box using the <select> tag.
*/
sablono.core.drop_down8417 = (function() {
var drop_down8417 = null;
var drop_down8417__2 = (function (name,options){return drop_down8417.call(null,name,options,null);
});
var drop_down8417__3 = (function (name,options,selected){return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"select","select",4402849902),new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"name","name",1017277949),sablono.core.make_name.call(null,name),new cljs.core.Keyword(null,"id","id",1013907597),sablono.core.make_id.call(null,name)], null),sablono.core.select_options.call(null,options,selected)], null);
});
drop_down8417 = function(name,options,selected){
switch(arguments.length){
case 2:
return drop_down8417__2.call(this,name,options);
case 3:
return drop_down8417__3.call(this,name,options,selected);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
drop_down8417.cljs$core$IFn$_invoke$arity$2 = drop_down8417__2;
drop_down8417.cljs$core$IFn$_invoke$arity$3 = drop_down8417__3;
return drop_down8417;
})()
;
sablono.core.drop_down = sablono.core.wrap_attrs.call(null,sablono.core.drop_down8417);
/**
* Creates a text area element.
*/
sablono.core.text_area8418 = (function() {
var text_area8418 = null;
var text_area8418__1 = (function (name){return text_area8418.call(null,name,null);
});
var text_area8418__2 = (function (name,value){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"textarea","textarea",4305627820),new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"name","name",1017277949),sablono.core.make_name.call(null,name),new cljs.core.Keyword(null,"id","id",1013907597),sablono.core.make_id.call(null,name),new cljs.core.Keyword(null,"value","value",1125876963),value], null)], null);
});
text_area8418 = function(name,value){
switch(arguments.length){
case 1:
return text_area8418__1.call(this,name);
case 2:
return text_area8418__2.call(this,name,value);
}
throw(new Error('Invalid arity: ' + arguments.length));
};
text_area8418.cljs$core$IFn$_invoke$arity$1 = text_area8418__1;
text_area8418.cljs$core$IFn$_invoke$arity$2 = text_area8418__2;
return text_area8418;
})()
;
sablono.core.text_area = sablono.core.wrap_attrs.call(null,sablono.core.text_area8418);
/**
* Creates a label for an input field with the supplied name.
*/
sablono.core.label8419 = (function label8419(name,text){return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"label","label",1116631654),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"htmlFor","htmlFor",2249940112),sablono.core.make_id.call(null,name)], null),text], null);
});
sablono.core.label = sablono.core.wrap_attrs.call(null,sablono.core.label8419);
/**
* Creates a submit button.
*/
sablono.core.submit_button8420 = (function submit_button8420(text){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"input","input",1114262332),new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"type","type",1017479852),"submit",new cljs.core.Keyword(null,"value","value",1125876963),text], null)], null);
});
sablono.core.submit_button = sablono.core.wrap_attrs.call(null,sablono.core.submit_button8420);
/**
* Creates a form reset button.
*/
sablono.core.reset_button8421 = (function reset_button8421(text){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"input","input",1114262332),new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"type","type",1017479852),"reset",new cljs.core.Keyword(null,"value","value",1125876963),text], null)], null);
});
sablono.core.reset_button = sablono.core.wrap_attrs.call(null,sablono.core.reset_button8421);
/**
* Create a form that points to a particular method and route.
* e.g. (form-to [:put "/post"]
* ...)
* @param {...*} var_args
*/
sablono.core.form_to8422 = (function() { 
var form_to8422__delegate = function (p__8423,body){var vec__8425 = p__8423;var method = cljs.core.nth.call(null,vec__8425,0,null);var action = cljs.core.nth.call(null,vec__8425,1,null);var method_str = clojure.string.upper_case.call(null,cljs.core.name.call(null,method));var action_uri = sablono.util.to_uri.call(null,action);return cljs.core.vec.call(null,cljs.core.concat.call(null,((cljs.core.contains_QMARK_.call(null,new cljs.core.PersistentHashSet(null, new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"get","get",1014006472),null,new cljs.core.Keyword(null,"post","post",1017351186),null], null), null),method))?new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"form","form",1017053238),new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"method","method",4231316563),method_str,new cljs.core.Keyword(null,"action","action",3885920680),action_uri], null)], null):new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"form","form",1017053238),new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"method","method",4231316563),"POST",new cljs.core.Keyword(null,"action","action",3885920680),action_uri], null),sablono.core.hidden_field.call(null,"_method",method_str)], null)),body));
};
var form_to8422 = function (p__8423,var_args){
var body = null;if (arguments.length > 1) {
  body = cljs.core.array_seq(Array.prototype.slice.call(arguments, 1),0);} 
return form_to8422__delegate.call(this,p__8423,body);};
form_to8422.cljs$lang$maxFixedArity = 1;
form_to8422.cljs$lang$applyTo = (function (arglist__8426){
var p__8423 = cljs.core.first(arglist__8426);
var body = cljs.core.rest(arglist__8426);
return form_to8422__delegate(p__8423,body);
});
form_to8422.cljs$core$IFn$_invoke$arity$variadic = form_to8422__delegate;
return form_to8422;
})()
;
sablono.core.form_to = sablono.core.wrap_attrs.call(null,sablono.core.form_to8422);

//# sourceMappingURL=core.js.map