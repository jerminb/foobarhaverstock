package com.e.foobar

import kotlinx.serialization.Serializable

@Serializable
data class Play (
    var passes: Int,
    var shots: Int,
    var carries: Int,
    var crosses: Int
)