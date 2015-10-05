//
//  HomePageTableView.swift
//  SapphireDesign
//
//  Created by gxwang on 15/8/29.
//  Copyright (c) 2015年 sapphire. All rights reserved.
//

import Foundation
import UIKit

class HomePageTableView : UITableView ,UITableViewDataSource,UITableViewDelegate ,SaPullToRefreshDelegate{
    
    var reloading: Bool = false
    var pullRefreshView:SaPullToRefreshView!
    
    func initTableView() {
        self.backgroundColor = UIColor.clearColor()
        self.dataSource = self
        self.delegate = self
        
        self.registerNib(UINib(nibName: "HomePageTableViewCell", bundle: NSBundle.mainBundle()), forCellReuseIdentifier: "HomePageTableViewCell")

    }
    
    func initRefreshView() {
        if pullRefreshView == nil {
            pullRefreshView = SaPullToRefreshView(frame: CGRectMake(0, -self.frame.height, self.frame.width, self.frame.height))
            pullRefreshView.delegate = self
            self.addSubview(pullRefreshView)
        }
    }
    
    func numberOfSectionsInTableView(tableView: UITableView) -> Int {
        return 1
    }
    
    func tableView(tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return 10
    }
    
    func tableView(tableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCellWithIdentifier("HomePageTableViewCell") as! HomePageTableViewCell
        
        return cell
    }
    
    func tableView(tableView: UITableView, heightForRowAtIndexPath indexPath: NSIndexPath) -> CGFloat {
        return 80
    }
    
    
    func tableView(tableView: UITableView, didSelectRowAtIndexPath indexPath: NSIndexPath) {
        tableView.deselectRowAtIndexPath(indexPath, animated: true)
    }
    
    func reloadCollectionViewDataSource() {
        reloading = true
    }
    
    func pullToRefreshDidTrigger(view: SaPullToRefreshView) -> () {
        reloadCollectionViewDataSource()
        
        let delay = 2.0 * Double(NSEC_PER_SEC)
        let time  = dispatch_time(DISPATCH_TIME_NOW, Int64(delay))
        dispatch_after(time, dispatch_get_main_queue(), {
            self.reloading = false
            self.pullRefreshView.refreshScrollViewDataSourceDidFinishedLoading(self)
        })
    }
    
    func scrollViewDidScroll(scrollView: UIScrollView) {
        pullRefreshView?.refreshScrollViewDidScroll(scrollView)
    }
    
    func scrollViewDidEndDragging(scrollView: UIScrollView, willDecelerate decelerate: Bool) {
        pullRefreshView?.refreshScrollViewDidEndDragging(scrollView)
    }
    
    func pullToRefreshIsLoading(view: SaPullToRefreshView) -> Bool {
        return reloading
    }
    
    func pullToRefreshLastUpdated(view: SaPullToRefreshView) -> NSDate {
        return NSDate()
    }
    
}
