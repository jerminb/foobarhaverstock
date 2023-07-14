package com.e.foobar

import android.util.Log
import androidx.lifecycle.ViewModel

class FooBarViewModel: ViewModel() {
    var model: FooBarModel = FooBarModel(Play(0,0,0, 0), mutableListOf())

    init {
        Log.d("MainActivity", "FooBarViewModel created!")
    }

    override fun onCleared() {
        super.onCleared()
        Log.d("MainActivity", "FooBarViewModel destroyed!")
    }
    fun resetPlay() {
        model.playsList = mutableListOf()
        model.currentPlay = Play(0,0,0, 0)
    }
    fun getNextPlay() {
        model.playsList.add(model.currentPlay)
        model.currentPlay = Play(0,0,0, 0)
    }

    var currentPlayPasses: Int
        get() = model.currentPlay.passes
        set(value) {model.currentPlay.passes = value}

    var currentPlayCrosses: Int
        get() = model.currentPlay.crosses
        set(value) {model.currentPlay.crosses = value}

    var currentPlayCarries: Int
        get() = model.currentPlay.carries
        set(value) {model.currentPlay.carries = value}

    var currentPlayShots: Int
        get() = model.currentPlay.shots
        set(value) {model.currentPlay.shots = value}

    val playsLenght: Int
        get() = model.playsList.size

    fun incrementCurrentPlay(action: PlayAction) {
        when(action){
            PlayAction.PASS -> ++model.currentPlay.passes
            PlayAction.CARRY -> ++model.currentPlay.carries
            PlayAction.CROSS -> ++model.currentPlay.crosses
            PlayAction.SHOT -> ++model.currentPlay.shots
        }
    }
}