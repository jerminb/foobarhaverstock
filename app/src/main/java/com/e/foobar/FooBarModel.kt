package com.e.foobar

import kotlinx.serialization.Serializable

@Serializable
data class FooBarModel (
    var currentPlay: Play,
    var playsList: MutableList<Play>
)