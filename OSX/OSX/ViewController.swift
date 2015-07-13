//
//  ViewController.swift
//  OSX
//
//  Created by gxwang on 15/7/11.
//  Copyright (c) 2015年 gxwang. All rights reserved.
//

import Cocoa

class ViewController: NSViewController {

    @IBOutlet weak var btn: NSButton!
    @IBOutlet weak var text: NSTextField!
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }

    override var representedObject: AnyObject? {
        didSet {
        // Update the view, if already loaded.
        }
    }

    @IBAction func click(sender: AnyObject) {
        
        println("hello")
        
        text.stringValue = "hello"
    }

}

