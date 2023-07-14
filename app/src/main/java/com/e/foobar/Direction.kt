package com.e.foobar

enum class Direction {
    up, down, left, right;

    companion object {
        /**
         * Returns a direction given an angle.
         * Directions are defined as follows:
         *
         * Up: [45, 135]
         * Right: [0,45] and [315, 360]
         * Down: [225, 315]
         * Left: [135, 225]
         *
         * @param angle an angle from 0 to 360 - e
         * @return the direction of an angle
         */
        fun fromAngle(angle: Double): Direction {
            return if (inRange(angle, 45f, 135f)) {
                up
            } else if (inRange(angle, 0f, 45f) || inRange(angle, 315f, 360f)) {
                right
            } else if (inRange(angle, 225f, 315f)) {
                down
            } else {
                left
            }
        }

        /**
         * @param angle an angle
         * @param init the initial bound
         * @param end the final bound
         * @return returns true if the given angle is in the interval [init, end).
         */
        private fun inRange(angle: Double, init: Float, end: Float): Boolean {
            return (angle >= init) && (angle < end)
        }
    }
}