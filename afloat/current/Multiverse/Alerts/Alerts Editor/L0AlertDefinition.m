//
//  L0AlertDefinition.m
//  Alerts Editor
//
//  Created by ∞ on 09/11/07.
//  Copyright 2007 __MyCompanyName__. All rights reserved.
//

#import "L0AlertDefinition.h"
#import "NSAlert+L0Alert.h"

#define L0SetError(error, init) \
if (error) \
*(error) = (init);

static inline NSString* L0Capitalize(NSString* prefix, NSString* str) {
	return [NSString stringWithFormat:@"%@%@%@",
			prefix,
			[[str substringToIndex:1] capitalizedString], [str substringFromIndex:1]];
}

@implementation L0AlertDefinition

@synthesize message;
@synthesize informativeText;
@synthesize firstButton;
@synthesize secondButton;
@synthesize thirdButton;

@synthesize helpAnchor;
@synthesize showsSuppressionButton;

@synthesize iconName;

- (id) initWithUndoManager:(NSUndoManager*) mgr {
	if (self = [super init])
		_undoManager = mgr;
	
	return self;
}

- (void) setValue:(id) value forKey:(NSString*) key {
	[_undoManager registerUndoWithTarget:self selector:NSSelectorFromString(L0Capitalize(@"set", key)) object:[self valueForKey:key]];
	[super setValue:value forKey:key];
}

- (BOOL) readFromURL:(NSURL*) url error:(NSError**) error {
	NSDictionary* dict = [NSDictionary dictionaryWithContentsOfURL:url];
	if (!dict) {
		L0SetError(error,
				   [NSError errorWithDomain:NSPOSIXErrorDomain code:EIO userInfo:nil]);
		return NO;
	}
	
	self.message = [dict objectForKey:kL0AlertMessage];
	self.informativeText = [dict objectForKey:kL0AlertInformativeText];
	
	NSArray* buttons = [dict objectForKey:kL0AlertButtons];
	int i = 0;
	for (NSString* button in buttons) {
		switch (i) {
			case 0:
				self.firstButton = button;
				break;
			case 1:
				self.secondButton = button;
				break;
			case 2:
				self.thirdButton = button;
				break;
		}
		
		i++;
		if (i > 2) break;
	}
	
	self.helpAnchor = [dict objectForKey:kL0AlertHelpAnchor];
	self.showsSuppressionButton = [[dict objectForKey:kL0AlertShowsSuppressionButton] boolValue];
	self.iconName = [dict objectForKey:kL0AlertIconName];
	
	return YES;
}

- (BOOL) writeToURL:(NSURL*) url error:(NSError**) error {
	if (![[self alertSettingsDictionary] writeToURL:url atomically:YES]) {
		L0SetError(error, [NSError errorWithDomain:NSPOSIXErrorDomain code:EIO userInfo:nil]);
		return NO;
	} else
		return YES;
}

- (NSDictionary*) alertSettingsDictionary {
	NSMutableDictionary* dict = [NSMutableDictionary dictionary];
	
	if (self.message)
		[dict setObject:self.message forKey:kL0AlertMessage];
	
	if (self.informativeText)
		[dict setObject:self.informativeText forKey:kL0AlertInformativeText];
	
	NSMutableArray* array = [NSMutableArray array];
	if (self.firstButton && ![self.firstButton isEqualToString:@""]) {
		[array addObject:self.firstButton];
		if (self.secondButton && ![self.secondButton isEqualToString:@""]) {
			[array addObject:self.secondButton];
			if (self.thirdButton && ![self.thirdButton isEqualToString:@""])
				[array addObject:self.thirdButton];
		}
	}
	L0Log(@"first = %@, second = %@, third = %@, buttons array = %@", firstButton, secondButton, thirdButton, array);
	[dict setObject:array forKey:kL0AlertButtons];
	
	if (self.helpAnchor && ![self.helpAnchor isEqualToString:@""])
		[dict setObject:self.helpAnchor forKey:kL0AlertHelpAnchor];
	
	[dict setObject:[NSNumber numberWithBool:self.showsSuppressionButton] forKey:kL0AlertShowsSuppressionButton];
	
	if (self.iconName && ![self.iconName isEqualToString:@""])
		[dict setObject:self.iconName forKey:kL0AlertIconName];
	
	return [NSDictionary dictionaryWithDictionary:dict];
}

@end
