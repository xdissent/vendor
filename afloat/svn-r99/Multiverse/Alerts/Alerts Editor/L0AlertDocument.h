//
//  L0AlertDocument.h
//  Alerts Editor
//
//  Created by ∞ on 09/11/07.
//  Copyright Emanuele Vulcano 2007 . All rights reserved.
//


#import <Cocoa/Cocoa.h>
#import "L0AlertDefinition.h"

@interface L0AlertDocument : NSDocument {
	L0AlertDefinition* definition;
	BOOL _alertIsShowing;
}

@property L0AlertDefinition* definition;

- (IBAction) testAlert:(id) sender;
- (BOOL) _canShowTestAlertUsingDefinitionContents:(BOOL) usingContents;
- (BOOL) exportStringsWithUserInteraction:(NSString*) to;

@end
