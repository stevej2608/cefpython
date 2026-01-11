// Copyright (c) 2016 CEF Python, see the Authors file.
// All rights reserved. Licensed under BSD 3-clause license.
// Project website: https://github.com/cztomczak/cefpython

#pragma once

#include <X11/Xlib.h>
#include <gtk/gtk.h>
#include <gdk/gdkx.h>

#include "include/cef_browser.h"

// Ensure CEF_X11 is defined before including Linux types
#ifndef CEF_X11
#define CEF_X11 1
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Declare cef_get_xdisplay since it may not be properly exported
typedef struct _XDisplay Display;
Display* cef_get_xdisplay(void);

#ifdef __cplusplus
}
#endif

void InstallX11ErrorHandlers();
void SetX11WindowBounds(CefRefPtr<CefBrowser> browser,
                        int x, int y, int width, int height);
void SetX11WindowTitle(CefRefPtr<CefBrowser> browser, char* title);

GtkWindow* CefBrowser_GetGtkWindow(CefRefPtr<CefBrowser> browser);
XImage* CefBrowser_GetImage(CefRefPtr<CefBrowser> browser);
