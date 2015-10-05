//
//  MarketViewController.swift
//  SapphireDesign
//
//  Created by 冯 波 on 15/8/22.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

class MarketViewController : UIViewController,UIScrollViewDelegate
{
    //tabHeaderSegmentView
    var tabHeaderSegmentView:HeaderTabSegmentView!
    
    /*init clothMarketCollectionViewController*/
    var clothMarketCollectionViewController:UICollectionViewController = UIStoryboard(name: "Main", bundle: nil).instantiateViewControllerWithIdentifier("clothMarketCollectionViewID") as! UICollectionViewController
    
    var clothCollectionView:MarketCollectionView!
    
    /*init MaterialCollectionViewController*/
    var materialCollectionViewController:UICollectionViewController = UIStoryboard(name: "Main", bundle: nil).instantiateViewControllerWithIdentifier("materialCollectionViewControllerID") as! UICollectionViewController
    
    var materialCollectionView:MaterialCollectionView!
    

    //view will load
    override func viewDidLoad() {
        super.viewDidLoad()
        self.tabBarItem.title = "商城"
    
    }
    

    override func viewWillAppear(animated: Bool) {
        super.viewWillAppear(true)
        initTabHeaderView()
        initScrollViewMarket()
        
    }
    
    //init methods function of viewDidAppear
    func initTabHeaderView()
    {
        
        let headerTabSegmentHeight:CGFloat = CGFloat(Int(self.view.frame.width/8))
        tabHeaderSegmentView = HeaderTabSegmentView(frame: CGRectMake(0, 64, self.view.frame.width, headerTabSegmentHeight))
        self.view.addSubview(tabHeaderSegmentView)
    }
    
    //init the scrollView of the market
    
    func initScrollViewMarket()
    {
        let scrollViewStartY:CGFloat = CGFloat(Int(self.view.frame.width/8)) + 64
        let bottomTabBarControllerHeight:CGFloat = 47.0
        let scrollHeight:CGFloat = self.view.frame.height - scrollViewStartY
        let scrollView:UIScrollView = UIScrollView(frame: CGRectMake(0, scrollViewStartY, self.view.frame.width, scrollHeight))
        scrollView.backgroundColor = UIColor.blackColor()
        scrollView.pagingEnabled = true
        scrollView.showsHorizontalScrollIndicator = false
        scrollView.showsVerticalScrollIndicator = false
        scrollView.bounces = false
        scrollView.bouncesZoom = false
        scrollView.delegate = self
        self.view.addSubview(scrollView)
        
        let redView:UIView = UIView(frame: CGRectMake(0, 0, self.view.frame.width, scrollHeight - bottomTabBarControllerHeight))
        redView.backgroundColor = UIColor.whiteColor()
        initClothCollectionView(redView)
        
        
        let blueView:UIView = UIView(frame: CGRectMake(self.view.frame.width, 0, self.view.frame.width, scrollHeight - bottomTabBarControllerHeight))
        
        blueView.backgroundColor = UIColor.whiteColor()
        initMaterialCollectionView(blueView)
        
        scrollView.addSubview(redView)
        scrollView.addSubview(blueView)
        scrollView.contentSize = CGSizeMake(self.view.frame.width * 2, scrollHeight)
        
        tabHeaderSegmentView.scrollView = scrollView

    }
    //init basic info of clothCollectionView
    func initClothCollectionView(parentView:UIView)
    {
        
        clothCollectionView       = clothMarketCollectionViewController.collectionView as! MarketCollectionView
        clothCollectionView.frame = parentView.frame
        clothCollectionView.initOriginalParam()
        parentView.addSubview(clothCollectionView)
    }
    
    //init basic info of MaterialCollectionView
    func initMaterialCollectionView(parentView:UIView)
    {
        materialCollectionView = materialCollectionViewController.collectionView as! MaterialCollectionView
        //materialCollectionView.frame = parentView.frame
        materialCollectionView.frame = CGRectMake(0, 0, self.view.frame.width, self.view.frame.height)
        materialCollectionView.initOriginalParam()
        parentView.addSubview(materialCollectionView)
    }
    
    //UIScrollView Delegate methods
    func scrollViewDidEndDecelerating(scrollView: UIScrollView)
    {
        let page:Int = Int(scrollView.contentOffset.x / scrollView.frame.size.width)
        tabHeaderSegmentView.modifyButtonSelect(page)
    }

}
