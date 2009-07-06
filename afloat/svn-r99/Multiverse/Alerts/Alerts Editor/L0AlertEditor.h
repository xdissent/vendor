//
//  L0AlertEditor.h
//  Alerts Editor
//
//  Created by ∞ on 22/12/07.
//  Copyright 2007 __MyCompanyName__. All rights reserved.
//

#import <Cocoa/Cocoa.h>


@interface L0AlertEditor : NSObject {
	NSOpenPanel* _currentPanel;
	IBOutlet NSView* _accessoryView;
	NSArray* _files;
}

- (IBAction) massExportOfStrings:(id) sender;
- (IBAction) closeCurrentAndChooseAll:(id) sender;

@property(retain) NSOpenPanel* currentPanel;
@property(copy) NSArray* files;

@end
