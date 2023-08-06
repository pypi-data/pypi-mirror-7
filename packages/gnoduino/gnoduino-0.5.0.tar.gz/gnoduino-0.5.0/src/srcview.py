# Arduino python implementation
# Copyright (C) 2010-2012  Lucian Langa
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import gtk
import fnmatch

import gettext
_ = gettext.gettext

import gtksourceview2
import misc
import prefs
import time

import config
import ui

def get_lang_for_file(f):
	manager = gtksourceview2.language_manager_get_default()
	languages = gtksourceview2.LanguageManager.get_language_ids(manager)
	for l in languages:
		lang = manager.get_language(l)
		if lang == None: return None
		globs = gtksourceview2.Language.get_globs(lang)
		if globs == None: continue
		for p in globs:
			if fnmatch.fnmatch(f, p):
				return lang

def get_lang_for_content(content):
	mime = misc.get_mime_type(content)
	manager = gtksourceview2.language_manager_get_default()
	languages = gtksourceview2.LanguageManager.get_language_ids(manager)
	for l in languages:
		lang = manager.get_language(l)
		if lang == None: return None
		globs = gtksourceview2.Language.get_mime_types(lang)
		if globs == None: continue
		for p in globs:
			if p == mime:
				return lang

def instextCallback(b, iter, text, len) :
	cont = b.get_text(b.get_start_iter(), b.get_end_iter())
	lang = get_lang_for_content(cont)
	if lang != None:
		b.set_language(lang)
	config.cur_iter = -1

def insertText(text, line):
	page = ui.getCurrentPage()
	view = page.get_data("view")
	b = view.get_buffer()
	iter = b.get_iter_at_mark(b.get_insert())
	iter.set_line(line);
	t = ""
	for i in text:
		t = t + "#include <" + i + ">\n"
	t = t + "\n"
	b.insert(iter, t)

def updatePos(buffer, sb):
	sb.pop(1)
	iter = buffer.get_iter_at_mark(buffer.get_insert())
	row = iter.get_line();
	col = iter.get_line_offset();
	msg = "Ln %d, Col %d" % (row+1, col+1)
	sb.push(1, msg);

def moveCursorOffset(view, offset):
	b = view.get_buffer()
	mark = b.get_insert()
	iter = b.get_iter_at_mark(mark)
	iter.set_offset(offset);
	b.place_cursor(iter)
	b.ensure_highlight(b.get_iter_at_offset(offset), b.get_iter_at_offset(offset + 10))
	view.scroll_mark_onscreen(mark)

def markCb(buffer, iter, mark, data):
	updatePos(buffer, data)

def resetCursor(buffer):
	mark = buffer.get_insert()
	iter = buffer.get_iter_at_mark(mark)
	iter.set_line(0);
	buffer.place_cursor(iter)

def findText(widget, event, data=None):
	if event == -1 or (event.type == gtk.gdk.KEY_RELEASE and \
	(gtk.gdk.keyval_name(event.keyval) == 'Return' or \
	 gtk.gdk.keyval_name(event.keyval) == 'KP_Enter')):
		page = ui.getCurrentPage()
		view = page.get_data("view")
		b = view.get_buffer()
		mark = b.get_insert()
		iter = b.get_iter_at_mark(mark)
		search = widget.get_text()
		flags = 0
		if data[0].get_active() == False:
			flags = gtksourceview2.SEARCH_CASE_INSENSITIVE
		backwards = False
		if data[2].get_active() == True:
			backwards = True
		warp = False
		if data[3].get_active() == True:
			warp = True
		if config.cur_iter == -1:
			config.cur_iter = iter
		sb = ui.getGui().get_object("statusbar1")
		if warp:
			try:
				if backwards:
					s, e = gtksourceview2.iter_backward_search( \
						config.cur_iter, search, flags, limit=None)
					config.cur_iter = s
				else:
					s, e = gtksourceview2.iter_forward_search( \
						config.cur_iter, search, flags, limit=None)
					config.cur_iter = e
			except:
				if backwards:
					iter = b.get_iter_at_offset(-1)
					config.cur_iter = iter
					try:
						s, e = gtksourceview2.iter_backward_search( \
							config.cur_iter, search, flags, limit=None)
						config.cur_iter = s
					except: return
				else:
					iter = b.get_iter_at_offset(0)
					config.cur_iter = iter
					try:
						s, e = gtksourceview2.iter_forward_search( \
							config.cur_iter, search, flags=0, limit=None)
						config.cur_iter = e
					except: return
		else:
			if backwards:
				try:
					s, e = gtksourceview2.iter_backward_search( \
						config.cur_iter, search, flags, limit=None)
					config.cur_iter = s
				except:
					s = e = b.get_start_iter()
					b.select_range(s, e)
					misc.statusMessage(sb, _("'%s' not found.") % search)
					return
			else:
				try:
					s, e = gtksourceview2.iter_forward_search( \
						config.cur_iter, search, flags, limit=None)
					config.cur_iter = e
				except:
					s = e = b.get_end_iter()
					b.select_range(s, e)
					misc.statusMessage(sb, _("'%s' not found.") % search)
					return
		b.place_cursor(s)
		b.select_range(s, e)
		view.scroll_to_iter(s,0)


def replaceText(widget, event, data=None):
	if event == -1 or (event.type == gtk.gdk.KEY_RELEASE and \
	(gtk.gdk.keyval_name(event.keyval) == 'Return' or \
	 gtk.gdk.keyval_name(event.keyval) == 'KP_Enter')):
		a = config.cur_iter
		page = ui.getCurrentPage()
		view = page.get_data("view")
		b = view.get_buffer()
		mark = b.get_insert()
		iter = b.get_iter_at_mark(mark)
		search = data[4].get_text()
		flags = 0
		if data[0].get_active() == False:
			flags = gtksourceview2.SEARCH_CASE_INSENSITIVE
		backwards = False
		if data[2].get_active() == True:
			backwards = True
		warp = False
		if data[3].get_active() == True:
			warp = True
		if config.cur_iter == -1:
			config.cur_iter = iter
		sb = ui.getGui().get_object("statusbar1")
		if warp:
			try:
				if backwards:
					s, e = gtksourceview2.iter_backward_search( \
						config.cur_iter, search, flags, limit=None)
					config.cur_iter = s
				else:
					s, e = gtksourceview2.iter_forward_search( \
						config.cur_iter, search, flags, limit=None)
					config.cur_iter = e
			except:
				if backwards:
					iter = b.get_iter_at_offset(-1)
					config.cur_iter = iter
					try:
						s, e = gtksourceview2.iter_backward_search( \
							config.cur_iter, search, flags, limit=None)
						config.cur_iter = s
					except:
						config.cur_iter = a
						return
				else:
					iter = b.get_iter_at_line(0)
					config.cur_iter = iter
					try:
						s, e = gtksourceview2.iter_forward_search( \
							config.cur_iter, search, flags=0, limit=None)
						config.cur_iter = e
					except:
						config.cur_iter = a
						return
		else:
			if backwards:
				try:
					s, e = gtksourceview2.iter_backward_search( \
						config.cur_iter, search, flags, limit=None)
					config.cur_iter = s
				except:
					s = e = b.get_start_iter()
					b.select_range(s, e)
					misc.statusMessage(sb, _("'%s' not found.") % search)
					config.cur_iter = a
					return
			else:
				try:
					s, e = gtksourceview2.iter_forward_search( \
						config.cur_iter, search, flags, limit=None)
					config.cur_iter = e
				except:
					s = e = b.get_end_iter()
					b.select_range(s, e)
					misc.statusMessage(sb, _("'%s' not found.") % search)
					config.cur_iter = a
					return
		b.place_cursor(s)
		b.select_range(s, e)
		b.delete_selection(False, True)
		b.insert_at_cursor(data[5].get_text())

def replaceAll(widget, data=None):
	page = ui.getCurrentPage()
	view = page.get_data("view")
	b = view.get_buffer()
	mark = b.get_insert()
	iter = b.get_iter_at_mark(mark)
	search = widget.get_text()
	flags = 0
	repls=[]
	if data[0].get_active() == False:
		flags = gtksourceview2.SEARCH_CASE_INSENSITIVE
	if config.cur_iter == -1:
		config.cur_iter = iter
	sb = ui.getGui().get_object("statusbar1")
	s = b.get_start_iter()
	b.begin_user_action()
	b.place_cursor(s)
	rpls=0
	config.cur_iter = b.get_iter_at_line(0)
	while config.cur_iter <= b.get_end_iter():
		try:
			s, e = gtksourceview2.iter_forward_search( \
				config.cur_iter, search, flags, limit=None)
			e.forward_line()
		except:
			iter = b.get_iter_at_offset(0)
			config.cur_iter = iter
			try:
				s, e = gtksourceview2.iter_forward_search( \
					config.cur_iter, search, flags=0, limit=None)
				e.forward_line()
			except:
				misc.statusMessage(sb, _("A total of %s replacements made.") % rpls)
				return
		if s.get_line() not in repls:
			repls.append(s.get_line())
			rpls = rpls + 1
			b.delete(s, e)
			b.insert(s, data[5].get_text()+"\n")
			config.cur_iter = s
	b.end_user_action()
	misc.statusMessage(sb, _("A total of %s replacements made.") % rpls)

def createsrcview(status, f=None):
	sbuffer = gtksourceview2.Buffer()
	if f:
		content = file(f).read()
		sbuffer.set_language(get_lang_for_content(content))
		text = unicode(content, 'utf-8', 'ignore')
		sbuffer.set_text(text)
	else:
		manager = gtksourceview2.language_manager_get_default()
		sbuffer.set_language(manager.get_language("c"))
	sv = gtksourceview2.View(sbuffer)
	p = prefs.preferences()
	misc.set_widget_font(sv, config.cur_editor_font)
	manager = gtksourceview2.StyleSchemeManager()
	manager.append_search_path(misc.getArduinoUiPath())
	manager.force_rescan()
	scheme =  manager.get_scheme("arduino")
	sbuffer.set_style_scheme(scheme);
	sv.set_size_request(300, 100)
	sv.set_editable(True)
	sv.set_auto_indent(True)
	if config.show_numbers == 'true':
		sv.set_show_line_numbers(True)
	sv.set_cursor_visible(True)
	sv.set_wrap_mode(gtk.WRAP_CHAR)
	sv.set_right_margin_position(80)
	updatePos(sbuffer, status)
	sbuffer.connect("mark_set", markCb, status)
	sbuffer.connect("insert_text", instextCallback)
	sv.set_highlight_current_line(True)
	resetCursor(sbuffer)
	return sbuffer, sv
