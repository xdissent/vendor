//
//  L0AlertDocument.m
//  Alerts Editor
//
//  Created by ∞ on 09/11/07.
//  Copyright Emanuele Vulcano 2007 . All rights reserved.
//

#import "L0AlertDocument.h"
#import "NSAlert+L0Alert.h"

@implementation L0AlertDocument

@synthesize definition;

- (id) init {
    self = [super init];
    if (self)
		self.definition = [[L0AlertDefinition alloc] initWithUndoManager:[self undoManager]];
	
    return self;
}

- (NSString*) windowNibName {
    return @"L0AlertDocument";
}

- (void) windowControllerDidLoadNib:(NSWindowController*) aController {
    [super windowControllerDidLoadNib:aController];

	// ...
}

- (BOOL) writeToURL:(NSURL*) url ofType:(NSString*) typeName error:(NSError**) error {
	return [self.definition writeToURL:url error:error];
}

- (BOOL) readFromURL:(NSURL*) url ofType:(NSString*) typeName error:(NSError**) error {
	[[self undoManager] disableUndoRegistration];
    return [self.definition readFromURL:url error:error];
	[[self undoManager] enableUndoRegistration];
}

- (IBAction) testAlert:(id) sender {
	NSWindow* wnd = [self windowForSheet]; // igh
	[wnd endEditingFor:[wnd firstResponder]];
	
	if (![self _canShowTestAlertUsingDefinitionContents:YES]) { NSBeep(); return; }
	
	NSAlert* alert = [NSAlert alertWithContentsOfDictionary:self.definition.alertSettingsDictionary name:nil bundle:nil];
	_alertIsShowing = YES;
	[alert beginSheetModalForWindow:[self windowForSheet] modalDelegate:self didEndSelector:@selector(_didEndAlert:result:contextInfo:) contextInfo:NULL];
}

- (BOOL) _canShowTestAlertUsingDefinitionContents:(BOOL) usingContents {
	return !_alertIsShowing &&
		(!usingContents || (self.definition.message && self.definition.informativeText));
}

- (void) _didEndAlert:(NSAlert*) alert result:(int) result contextInfo:(void*) ctx {
	_alertIsShowing = NO;
}

- (BOOL) validateMenuItem:(NSMenuItem*) menuItem {
	if ([menuItem action] == @selector(testAlert:))
		return [self _canShowTestAlertUsingDefinitionContents:NO];
	else
		return [super validateMenuItem:menuItem];
}

- (void) exportStringsFile:(id) sender {
	NSSavePanel* save = [NSSavePanel savePanel];
	[save setRequiredFileType:@"strings"];
	[save setMessage:@"Choose where to save the strings file for this alert:"];
	NSString* file = [[[[[self fileURL] path] lastPathComponent] stringByDeletingPathExtension] stringByAppendingPathExtension:@"strings"];
	NSLog(@"file");
	if (!file) file = @"Untitled.strings";
	[save beginSheetForDirectory:nil file:file modalForWindow:[self windowForSheet] modalDelegate:self didEndSelector:@selector(_exportStringsSaveDidEnd:result:contextInfo:) contextInfo:NULL];
}

- (void) _exportStringsSaveDidEnd:(NSSavePanel*) s result:(NSInteger) result contextInfo:(void*) nothing {
	if (result == NSCancelButton) return;
	
	[self exportStringsWithUserInteraction:[s filename]];
}

- (BOOL) exportStringsWithUserInteraction:(NSString*) path {
	NSMutableDictionary* dict = [NSMutableDictionary dictionary];
	if (definition.message && ![definition.message isEqual:@""])
		[dict setObject:definition.message forKey:definition.message];
	if (definition.informativeText && ![definition.informativeText isEqual:@""])
		[dict setObject:definition.informativeText forKey:definition.informativeText];
	if (definition.firstButton && ![definition.firstButton isEqual:@""])
		[dict setObject:definition.firstButton forKey:definition.firstButton];
	if (definition.secondButton && ![definition.secondButton isEqual:@""])
		[dict setObject:definition.secondButton forKey:definition.secondButton];
	if (definition.thirdButton && ![definition.thirdButton isEqual:@""])
		[dict setObject:definition.thirdButton forKey:definition.thirdButton];
	
	NSError* err = nil;
	if (![[dict descriptionInStringsFileFormat] writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:&err]) {
		[path retain];
		[self presentError:err modalForWindow:[self windowForSheet] delegate:self didPresentSelector:@selector(_exportStringsErrorResolved:contextInfo:) contextInfo:path];
		return NO;
	}
	
	return YES;
}

- (void) _exportStringsErrorResolved:(BOOL) resolved contextInfo:(void*) pathPtr {
	[(id)pathPtr autorelease];
	if (resolved)
		[self exportStringsWithUserInteraction:(NSString*)pathPtr];
}

@end
