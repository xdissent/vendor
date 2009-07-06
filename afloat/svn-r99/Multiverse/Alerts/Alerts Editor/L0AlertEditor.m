//
//  L0AlertEditor.m
//  Alerts Editor
//
//  Created by ∞ on 22/12/07.
//  Copyright 2007 __MyCompanyName__. All rights reserved.
//

#import "L0AlertEditor.h"
#import "L0AlertDocument.h"

@implementation L0AlertEditor

@synthesize currentPanel = _currentPanel, files = _files;

- (IBAction) massExportOfStrings:(id) sender {
	NSOpenPanel* open = [NSOpenPanel openPanel];
	[open setMessage:@"Choose any number of alert files to be exported:"];
	[open setPrompt:@"Choose"];
	[open setRequiredFileType:@"alert"];
	[open setAllowsMultipleSelection:YES];
	[open setAccessoryView:_accessoryView];
	self.currentPanel = open;
	self.files = nil;
	
	if ([open runModal] == NSCancelButton && !self.files) return;
	self.currentPanel = nil;
	
	NSArray* arr;
	if (!self.files)
		arr = [[[open filenames] copy] autorelease];
	else
		arr = [[self.files copy] autorelease];
	self.files = nil;
	
	L0Log(@"%@", arr);
	
	open = [NSOpenPanel openPanel];
	[open setMessage:@"Choose where to export the new strings files:"];
	[open setPrompt:@"Export"];
	[open setCanChooseFiles:NO];
	[open setCanChooseDirectories:YES];
	
	if ([open runModal] == NSCancelButton) return;
	
	for (NSString* path in arr) {
		NSError* err = nil;
		L0AlertDocument* doc;
		do {
			doc = [[NSDocumentController sharedDocumentController] openDocumentWithContentsOfURL:[NSURL fileURLWithPath:path] display:YES error:&err];
			if (err && ![NSApp presentError:err]) return;
		} while (err != nil);
		
		NSString* target = [[open filename] stringByAppendingPathComponent:[[[path lastPathComponent] stringByDeletingPathExtension] stringByAppendingPathExtension:@"strings"]];
		if ([doc exportStringsWithUserInteraction:target])
			[doc close];
	}
}

- (IBAction) closeCurrentAndChooseAll:(id) sender {
	NSString* dir = [self.currentPanel directory];
	if (dir) {
		NSFileManager* fm = [NSFileManager defaultManager];
		NSMutableArray* arr = [NSMutableArray array];
		for (NSString* item in [fm directoryContentsAtPath:dir]) {
			if ([[item pathExtension] isEqual:@"alert"])
				[arr addObject:[dir stringByAppendingPathComponent:item]];
		}
		
		self.files = arr;
		[self.currentPanel cancel:self];
	} else
		NSBeep();
}
	
@end
