//
//  EFAnimationViewController.h
//  SapphireDesign
//
//  Created by 波 冯 on 15/9/3.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface EFAnimationViewController : UIViewController

@end

@protocol EFItemViewDelegate <NSObject>

- (void)didTapped:(NSInteger)index;

@end



@interface EFItemView : UIButton

@property (nonatomic, weak) id <EFItemViewDelegate>delegate;

- (instancetype)initWithNormalImage:(NSString *)normal highlightedImage:(NSString *)highlighted tag:(NSInteger)tag title:(NSString *)title;

@end