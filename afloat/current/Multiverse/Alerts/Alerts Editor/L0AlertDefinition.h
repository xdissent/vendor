//
//  L0AlertDefinition.h
//  Alerts Editor
//
//  Created by ∞ on 09/11/07.
//  Copyright 2007 __MyCompanyName__. All rights reserved.
//

#import <Cocoa/Cocoa.h>


@interface L0AlertDefinition : NSObject {
	NSString* message;
	NSString* informativeText;
	NSString* firstButton;
	NSString* secondButton;
	NSString* thirdButton;
    
	NSString* helpAnchor;
	BOOL showsSuppressionButton;
    
	NSString* iconName;
	
	NSUndoManager* _undoManager;
}

- (id) initWithUndoManager:(NSUndoManager*) mgr;

@property(copy) NSString* message;
@property(copy) NSString* informativeText;
@property(copy) NSString* firstButton;
@property(copy) NSString* secondButton;
@property(copy) NSString* thirdButton;

@property(copy) NSString* helpAnchor;
@property(assign) BOOL showsSuppressionButton;

@property(copy) NSString* iconName;

@property(readonly) NSDictionary* alertSettingsDictionary;

- (BOOL) readFromURL:(NSURL*) url error:(NSError**) error;
- (BOOL) writeToURL:(NSURL*) url error:(NSError**) error;

@end
