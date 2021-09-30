import { Component, OnInit } from '@angular/core';
import { ses } from '../hero';
import {HttpClient , HttpHeaders, HttpClientModule} from '@angular/common/http';

import { Injectable, OnDestroy } from '@angular/core';
import { Observable, timer, Subscription, Subject } from 'rxjs';

import { switchMap, tap, share, retry, takeUntil } from 'rxjs/operators';

import { HeroService , CurrencyInfo} from './hero.service';




@Component({
  selector: 'app-heroes',
  templateUrl: './heroes.component.html',
  styleUrls: ['./heroes.component.css']
})
export class HeroesComponent implements OnInit {



  ngOnInit(): void {


  //   function tick() {
  //      //get the mins of the current time
  //      var secs = new Date().getSeconds();
  //      console.log(secs);
  //      if (secs == 0) {
  //        secs = secs;
 //    }

  }

  //setInterval(tick, 1000);

  //this.httpClient.get('http://127.0.0.1:5000/').subscribe(Response => {

      // If response comes hideloader() function is called
      // to hide that loader
  //    if(Response){

  //    }
 //     console.log(Response)
  //    this.li=Response;
  //    this.lis=this.li.list;

  //    console.log(this.lis[0]["id"]);

  //  });

 // }
}
